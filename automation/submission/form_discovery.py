#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ULTRA-RESILIENT Playwright automation helper with LOCAL CAPTCHA solver.
Designed to NEVER fail catastrophically and ALWAYS return valid JSON.
"""

from __future__ import annotations

# CRITICAL: Write to file FIRST as heartbeat, then try stderr
import sys
import os
import time
from pathlib import Path

# Force unbuffered output
os.environ['PYTHONUNBUFFERED'] = '1'

# HEARTBEAT: Write to file immediately to confirm script is running
# Use custom tmp directory if available, otherwise use /tmp
try:
    # Try to use project-specific tmp directory first
    project_tmp = Path('/var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp')
    if project_tmp.exists() and os.access(project_tmp, os.W_OK):
        heartbeat_dir = project_tmp
    else:
        # Try to create it
        try:
            project_tmp.mkdir(parents=True, exist_ok=True)
            if os.access(project_tmp, os.W_OK):
                heartbeat_dir = project_tmp
            else:
                heartbeat_dir = Path('/tmp')
        except:
            heartbeat_dir = Path('/tmp')
    
    heartbeat_file = heartbeat_dir / f'python_script_heartbeat_{os.getpid()}.txt'
    with open(heartbeat_file, 'w') as f:
        f.write(f"Script started at {time.time()}\n")
        f.write(f"PID: {os.getpid()}\n")
        f.write(f"Heartbeat location: {heartbeat_file}\n")
        try:
            f.write(f"Path: {__file__}\n")
        except:
            f.write("Path: unknown\n")
        f.write(f"Python: {sys.version}\n")
        f.flush()
        os.fsync(f.fileno())  # Force write to disk
except Exception as e:
    # Even if file write fails, continue
    # Try fallback to /tmp
    try:
        heartbeat_file = f'/tmp/python_script_heartbeat_{os.getpid()}.txt'
        with open(heartbeat_file, 'w') as f:
            f.write(f"Script started at {time.time()}\n")
            f.write(f"PID: {os.getpid()}\n")
            f.write(f"Fallback location: {heartbeat_file}\n")
            f.flush()
            os.fsync(f.fileno())
    except:
        heartbeat_file = None
        pass

# Now try to write to stderr
try:
    # Force line buffering
    if hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(line_buffering=True)
        except:
            pass
    
    # Write startup message - use multiple methods
    msg1 = "=" * 80 + "\n"
    msg2 = "🚀 PYTHON SCRIPT STARTING\n"
    msg3 = "=" * 80 + "\n"
    
    sys.stderr.write(msg1)
    sys.stderr.flush()
    sys.stderr.write(msg2)
    sys.stderr.flush()
    sys.stderr.write(msg3)
    sys.stderr.flush()
    
    # Also use print
    print("=" * 80, file=sys.stderr, flush=True)
    print("🚀 PYTHON SCRIPT STARTING", file=sys.stderr, flush=True)
    print("=" * 80, file=sys.stderr, flush=True)
    
    sys.stderr.write(f"Python version: {sys.version}\n")
    sys.stderr.flush()
    
    try:
        script_path = __file__
        sys.stderr.write(f"Script path: {script_path}\n")
        sys.stderr.flush()
    except:
        sys.stderr.write("Script path: (unknown)\n")
        sys.stderr.flush()
    
    sys.stderr.write("\n🔄 Starting imports...\n")
    sys.stderr.flush()
    
    # Update heartbeat file
    try:
        if heartbeat_file:
            # Handle both Path objects and strings
            if isinstance(heartbeat_file, Path):
                if heartbeat_file.exists():
                    with open(heartbeat_file, 'a') as f:
                        f.write("Startup messages sent to stderr\n")
                        f.flush()
                        os.fsync(f.fileno())
            else:
                # String path
                if os.path.exists(str(heartbeat_file)):
                    with open(heartbeat_file, 'a') as f:
                        f.write("Startup messages sent to stderr\n")
                        f.flush()
                        os.fsync(f.fileno())
    except:
        pass
        
except Exception as e:
    # Write error to file
    try:
        # Try project tmp directory first
        error_file = Path('/var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_startup_error.txt')
        try:
            error_file.parent.mkdir(parents=True, exist_ok=True)
        except:
            pass
        
        if error_file.parent.exists() and os.access(error_file.parent, os.W_OK):
            with open(error_file, 'w') as f:
                f.write(f"Failed to print to stderr: {e}\n")
                import traceback
                f.write(traceback.format_exc())
                f.flush()
                os.fsync(f.fileno())
        else:
            # Fallback to /tmp
            with open('/tmp/python_startup_error.txt', 'w') as f:
                f.write(f"Failed to print to stderr: {e}\n")
                import traceback
                f.write(traceback.format_exc())
                f.flush()
                os.fsync(f.fileno())
    except:
        pass

# Update heartbeat after each import
try:
    import argparse
    sys.stderr.write("✅ argparse imported\n")
    sys.stderr.flush()
    try:
        if heartbeat_file:
            # Handle both Path objects and strings
            if isinstance(heartbeat_file, Path):
                if heartbeat_file.exists():
                    with open(heartbeat_file, 'a') as f:
                        f.write("argparse imported\n")
                        f.flush()
            else:
                # String path
                if os.path.exists(str(heartbeat_file)):
                    with open(heartbeat_file, 'a') as f:
                        f.write("argparse imported\n")
                        f.flush()
    except:
        pass
    
    import asyncio
    sys.stderr.write("✅ asyncio imported\n")
    sys.stderr.flush()
    
    import json
    sys.stderr.write("✅ json imported\n")
    sys.stderr.flush()
    
    import os
    sys.stderr.write("✅ os imported\n")
    sys.stderr.flush()
    
    import time
    sys.stderr.write("✅ time imported\n")
    sys.stderr.flush()
    
    import traceback
    sys.stderr.write("✅ traceback imported\n")
    sys.stderr.flush()
    
    import random
    import base64
    import hashlib
    import subprocess
    import signal
    from pathlib import Path
    from typing import Any, Dict, List, Optional, Union
    from urllib.parse import urlparse
    
    sys.stderr.write("✅ All basic imports successful\n")
    sys.stderr.flush()
    
    # Final heartbeat update
    try:
        if heartbeat_file:
            # Handle both Path objects and strings
            if isinstance(heartbeat_file, Path):
                if heartbeat_file.exists():
                    with open(heartbeat_file, 'a') as f:
                        f.write("All imports successful\n")
                        f.write(f"Ready to start automation\n")
                        f.flush()
                        os.fsync(f.fileno())
            else:
                # String path
                if os.path.exists(str(heartbeat_file)):
                    with open(heartbeat_file, 'a') as f:
                        f.write("All imports successful\n")
                        f.write(f"Ready to start automation\n")
                        f.flush()
                        os.fsync(f.fileno())
    except:
        pass
        
except ImportError as e:
    error_msg = f"❌ IMPORT ERROR: {str(e)}\n"
    sys.stderr.write(error_msg)
    sys.stderr.flush()
    try:
        # Try project tmp directory first
        error_file = Path('/var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_import_error.txt')
        try:
            error_file.parent.mkdir(parents=True, exist_ok=True)
        except:
            pass
        
        if error_file.parent.exists() and os.access(error_file.parent, os.W_OK):
            with open(error_file, 'w') as f:
                f.write(error_msg)
                import traceback
                f.write(traceback.format_exc())
        else:
            # Fallback to /tmp
            with open('/tmp/python_import_error.txt', 'w') as f:
                f.write(error_msg)
                import traceback
                f.write(traceback.format_exc())
    except:
        pass
    sys.exit(1)
except Exception as e:
    error_msg = f"❌ ERROR during imports: {str(e)}\n"
    sys.stderr.write(error_msg)
    sys.stderr.flush()
    import traceback
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    try:
        # Try project tmp directory first
        error_file = Path('/var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_import_error.txt')
        try:
            error_file.parent.mkdir(parents=True, exist_ok=True)
        except:
            pass
        
        if error_file.parent.exists() and os.access(error_file.parent, os.W_OK):
            with open(error_file, 'w') as f:
                f.write(error_msg)
                f.write(traceback.format_exc())
        else:
            # Fallback to /tmp
            with open('/tmp/python_import_error.txt', 'w') as f:
                f.write(error_msg)
                f.write(traceback.format_exc())
    except:
        pass
    sys.exit(1)

# ULTRA-RESILIENT ENVIRONMENT SETUP
def setup_ultra_resilient_environment():
    """Set up environment with multiple fallbacks to prevent any failure."""
    try:
        # Force unbuffered output
        os.environ.setdefault('PYTHONUNBUFFERED', '1')
        if sys.platform == 'win32':
            os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
        
        # Add script directory to path with multiple fallbacks
        _script_dir = None
        for attempt in [
            lambda: Path(__file__).parent.absolute(),
            lambda: Path.cwd(),
            lambda: Path(sys.executable).parent if sys.executable else Path.cwd(),
            lambda: Path.home()
        ]:
            try:
                _script_dir = attempt()
                if _script_dir and _script_dir.exists():
                    break
            except:
                pass
        
        if not _script_dir:
            _script_dir = Path.cwd()
            
        script_dir_str = str(_script_dir)
        if script_dir_str not in sys.path:
            sys.path.insert(0, script_dir_str)
            
        return True
    except Exception:
        return False  # Even if setup fails, we continue

# Initialize environment
setup_ultra_resilient_environment()

# GLOBAL FALLBACKS - Multiple layers of redundancy
ULTRA_FALLBACK_RESULTS = [
    {
        "status": "error",
        "message": "Script encountered an unrecoverable error",
        "url": "unknown",
        "error_type": "fallback_1",
        "recovered": True,
        "timestamp": time.time()
    },
    {
        "status": "failed",
        "message": "Backup fallback result",
        "url": "unknown", 
        "error_type": "fallback_2",
        "recovered": True,
        "timestamp": time.time()
    },
    '{"status": "error", "message": "JSON fallback", "recovered": true}'
]

def get_ultimate_fallback_result(url: str = "unknown") -> str:
    """Return a valid JSON result no matter what."""
    try:
        fallback = ULTRA_FALLBACK_RESULTS[0].copy()
        fallback["url"] = url
        fallback["timestamp"] = time.time()
        return json.dumps(fallback)
    except:
        try:
            return ULTRA_FALLBACK_RESULTS[2]  # Pre-formatted JSON string
        except:
            return '{"status": "error", "message": "ultimate fallback", "recovered": true}'

def ultra_safe_log_print(*args, **kwargs):
    """ULTRA-RESILIENT logging - cannot fail under any circumstances."""
    MAX_ATTEMPTS = 3
    
    for attempt in range(MAX_ATTEMPTS):
        try:
            # Safely get output stream - ALWAYS use stderr for logs so they're captured
            output_file = None
            for stream in [sys.stderr, sys.stdout]:
                try:
                    if (hasattr(stream, 'closed') and not stream.closed and 
                        hasattr(stream, 'write')):
                        output_file = stream
                        break
                except:
                    continue
            
            if not output_file:
                # Ultimate fallback - open a temporary file
                try:
                    output_file = open(os.devnull, 'w', encoding='utf-8', errors='ignore')
                except:
                    return  # Give up silently
            
            # Safely prepare message
            safe_args = []
            for arg in args:
                try:
                    if isinstance(arg, (str, int, float, bool)):
                        safe_args.append(str(arg))
                    else:
                        safe_args.append(f"[{type(arg).__name__}]")
                except:
                    safe_args.append("[unprintable]")
            
            # Safely print to stderr (for logs) - use same non-blocking approach as safe_write
            # CRITICAL: Use select() to check if pipe is writable before writing to prevent blocking
            try:
                # Handle sep parameter
                sep = kwargs.get('sep', ' ')
                message = sep.join(str(arg) for arg in safe_args)
                
                # Handle end parameter (default is newline)
                end = kwargs.get('end', '\n')
                message += end
                
                # Check if stderr is a pipe (not TTY)
                is_pipe = not (hasattr(sys.stderr, 'isatty') and sys.stderr.isatty())
                
                # For pipes, check if writable before writing (non-blocking check)
                if is_pipe:
                    try:
                        import select
                        if hasattr(sys.stderr, 'fileno'):
                            fileno = sys.stderr.fileno()
                            # Check if file descriptor is writable (timeout 0 = non-blocking)
                            ready, _, _ = select.select([], [fileno], [], 0)
                            if fileno not in ready:
                                # Pipe buffer is full, but for logging we'll try a small delay and retry once
                                # This ensures important logs don't get completely lost
                                import time
                                time.sleep(0.01)  # Small delay to let buffer drain
                                # Try once more
                                ready, _, _ = select.select([], [fileno], [], 0)
                                if fileno not in ready:
                                    # Still full, but write anyway - better to have partial logs than none
                                    # The write might block briefly, but Node.js should read it
                                    pass
                    except (ImportError, OSError, ValueError):
                        # select not available or failed, try writing anyway
                        pass
                
                # Write the message
                try:
                    sys.stderr.write(message)
                except (IOError, OSError) as e:
                    # If write would block (EAGAIN/EWOULDBLOCK), try once more after brief delay
                    import errno
                    if hasattr(errno, 'EAGAIN') and e.errno == errno.EAGAIN:
                        import time
                        time.sleep(0.01)
                        try:
                            sys.stderr.write(message)
                        except:
                            pass  # Give up
                    elif hasattr(errno, 'EWOULDBLOCK') and e.errno == errno.EWOULDBLOCK:
                        import time
                        time.sleep(0.01)
                        try:
                            sys.stderr.write(message)
                        except:
                            pass  # Give up
                
                # Only flush if it's a TTY (terminal), not a pipe
                if not is_pipe:
                    try:
                        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
                            sys.stderr.flush()
                    except:
                        pass
            except:
                # Fallback to print if direct write fails
                try:
                    print(*safe_args, **{**kwargs, 'file': sys.stderr}, flush=False)  # Don't flush
                except:
                    pass
                
            break  # Success
            
        except Exception:
            if attempt == MAX_ATTEMPTS - 1:
                pass  # Silent failure - cannot log

class UltimateSafetyWrapper:
    """Wrap any operation to prevent any failure."""
    
    @staticmethod
    async def execute_async(operation, *args, default_return=None, max_retries=2, **kwargs):
        """Execute async operation with ultimate safety."""
        for attempt in range(max_retries + 1):
            try:
                result = await operation(*args, **kwargs)
                return result
            except Exception as e:
                if attempt == max_retries:
                    ultra_safe_log_print(f"⚠️  Operation failed after {max_retries + 1} attempts: {type(e).__name__}")
                    return default_return
                await asyncio.sleep(0.1 * (attempt + 1))
        return default_return
    
    @staticmethod
    def execute_sync(operation, *args, default_return=None, max_retries=2, **kwargs):
        """Execute sync operation with ultimate safety."""
        for attempt in range(max_retries + 1):
            try:
                result = operation(*args, **kwargs)
                return result
            except Exception as e:
                if attempt == max_retries:
                    ultra_safe_log_print(f"⚠️  Sync operation failed after {max_retries + 1} attempts: {type(e).__name__}")
                    return default_return
                time.sleep(0.1 * (attempt + 1))
        return default_return

class LocalCaptchaSolver:
    """
    ULTRA-RESILIENT LOCAL CAPTCHA solver - no external dependencies.
    Uses heuristic approaches to handle common CAPTCHA patterns.
    """
    
    def __init__(self, page=None):
        self.solved_tokens = {}
        self.page = page
        # Import UltimateLocalCaptchaSolver for real solving
        try:
            import sys
            from pathlib import Path
            parent_dir = Path(__file__).parent.parent
            if str(parent_dir) not in sys.path:
                sys.path.insert(0, str(parent_dir))
            from captcha_solver import UltimateLocalCaptchaSolver
            self.ultimate_solver = UltimateLocalCaptchaSolver(page=page)
        except Exception as e:
            ultra_safe_log_print(f"⚠️  Could not import UltimateLocalCaptchaSolver: {str(e)[:50]}")
            self.ultimate_solver = None
        ultra_safe_log_print("🔐 Initialized LOCAL CAPTCHA solver")
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Dict[str, Any]:
        """Solve reCAPTCHA v2 using comprehensive local strategies including audio challenge."""
        ultra_safe_log_print(f"🔐 Attempting LOCAL reCAPTCHA v2 solve for site key: {site_key[:20]}...")
        
        # Try using UltimateLocalCaptchaSolver for real solving (includes audio challenge)
        if self.ultimate_solver and self.page:
            try:
                # Validate page is still open
                try:
                    if self.page.is_closed():
                        ultra_safe_log_print("   ⚠️  Page is closed, cannot solve CAPTCHA")
                        return {
                            "token": None,
                            "response": None,
                            "site_key": site_key,
                            "solved_at": time.time(),
                            "method": "failed_page_closed"
                        }
                except:
                    pass
                
                self.ultimate_solver.page = self.page  # Ensure page is set
                ultra_safe_log_print("   🔄 Attempting comprehensive CAPTCHA solving (checkbox click, iframe interaction, audio challenge)...")
                
                # Check if challenge iframe already exists before solving
                try:
                    if self.page.is_closed():
                        return {
                            "token": None,
                            "response": None,
                            "site_key": site_key,
                            "solved_at": time.time(),
                            "method": "failed_page_closed"
                        }
                except:
                    pass
                
                challenge_exists = await self.page.evaluate("""
                    () => {
                        const challengeIframes = document.querySelectorAll('iframe[title*="challenge"], iframe[src*="bframe"]');
                        return challengeIframes.length > 0;
                    }
                """)
                if challenge_exists:
                    ultra_safe_log_print("   ⚠️  Challenge iframe already present - will attempt audio challenge solving")
                
                # Try comprehensive solving with timeout (60 seconds max to prevent consuming entire operation timeout)
                # If audio challenge requires ffmpeg and it's not available, it will fail quickly
                captcha_timeout = 60.0  # 60 seconds max for CAPTCHA solving
                result = await asyncio.wait_for(
                    self.ultimate_solver.solve_recaptcha_v2(site_key, page_url),
                    timeout=captcha_timeout
                )
                
                # Wait for token to appear after solving
                await asyncio.sleep(5)
                
                # Validate page is still open before checking token
                try:
                    if self.page.is_closed():
                        ultra_safe_log_print("   ⚠️  Page closed during CAPTCHA solving")
                        return {
                            "token": None,
                            "response": None,
                            "site_key": site_key,
                            "solved_at": time.time(),
                            "method": "failed_page_closed"
                        }
                except:
                    pass
                
                if result.get("success") and result.get("token"):
                    # Verify token is actually present in the page (not just generated)
                    try:
                        if self.page.is_closed():
                            return {
                                "token": None,
                                "response": None,
                                "site_key": site_key,
                                "solved_at": time.time(),
                                "method": "failed_page_closed"
                            }
                    except:
                        pass
                    
                    token_verified = await self.page.evaluate("""
                        () => {
                            const recaptchaResponse = document.querySelector('#g-recaptcha-response');
                            if (recaptchaResponse && recaptchaResponse.value) {
                                const token = recaptchaResponse.value;
                                // Check if it's a real token (not our fake format)
                                if (token.length > 20) {
                                    // Check if it's NOT our fake token format
                                    const isFakeToken = token.startsWith('03AOLTBLR_') && token.split('_').length === 3;
                                    return { 
                                        verified: true, 
                                        token: token, 
                                        length: token.length,
                                        isFakeToken: isFakeToken
                                    };
                                }
                            }
                            return { verified: false };
                        }
                    """)
                    
                    if token_verified.get("verified"):
                        if token_verified.get("isFakeToken"):
                            ultra_safe_log_print("⚠️  Token found but appears to be fake - challenge may not have been solved")
                            ultra_safe_log_print("   🔄 Re-attempting comprehensive solving with longer waits...")
                            # Try one more time with longer waits
                            await asyncio.sleep(5)
                            try:
                                result2 = await asyncio.wait_for(
                                    self.ultimate_solver.solve_recaptcha_v2(site_key, page_url),
                                    timeout=300.0
                                )
                                if result2.get("success") and result2.get("token"):
                                    await asyncio.sleep(5)
                                    token_verified2 = await self.page.evaluate("""
                                        () => {
                                            const recaptchaResponse = document.querySelector('#g-recaptcha-response');
                                            if (recaptchaResponse && recaptchaResponse.value) {
                                                const token = recaptchaResponse.value;
                                                const isFakeToken = token.startsWith('03AOLTBLR_') && token.split('_').length === 3;
                                                return { verified: true, token: token, isFakeToken: isFakeToken };
                                            }
                                            return { verified: false };
                                        }
                                    """)
                                    if token_verified2.get("verified") and not token_verified2.get("isFakeToken"):
                                        ultra_safe_log_print("✅ CAPTCHA solved with real token on retry!")
                                        return {
                                            "token": token_verified2.get("token"),
                                            "response": token_verified2.get("token"),
                                            "site_key": site_key,
                                            "solved_at": time.time(),
                                            "method": "comprehensive_local"
                                        }
                            except:
                                pass
                        
                        ultra_safe_log_print("✅ LOCAL CAPTCHA solved using comprehensive strategies (token verified in page)")
                        return {
                            "token": token_verified.get("token") or result.get("token"),
                            "response": token_verified.get("token") or result.get("token"),
                            "site_key": site_key,
                            "solved_at": time.time(),
                            "method": "comprehensive_local"
                        }
                    else:
                        ultra_safe_log_print("⚠️  Comprehensive solver returned token but it's not in the page - retrying...")
                        # Wait a bit and check again
                        await asyncio.sleep(5)
                        token_verified = await self.page.evaluate("""
                            () => {
                                const recaptchaResponse = document.querySelector('#g-recaptcha-response');
                                if (recaptchaResponse && recaptchaResponse.value) {
                                    const token = recaptchaResponse.value;
                                    if (token.length > 20) {
                                        return { verified: true, token: token };
                                    }
                                }
                                return { verified: false };
                            }
                        """)
                        if token_verified.get("verified"):
                            ultra_safe_log_print("✅ Token verified after retry!")
                            return {
                                "token": token_verified.get("token"),
                                "response": token_verified.get("token"),
                                "site_key": site_key,
                                "solved_at": time.time(),
                                "method": "comprehensive_local"
                            }
                elif not result.get("success"):
                    ultra_safe_log_print(f"⚠️  Comprehensive solver failed: {result.get('error', 'Unknown error')}")
                else:
                    ultra_safe_log_print("⚠️  Comprehensive solver did not return success - may need manual solving")
            except asyncio.TimeoutError:
                ultra_safe_log_print("⚠️  Comprehensive solving timed out (60s) - CAPTCHA may require manual solving")
                ultra_safe_log_print("   💡 Tip: Install ffmpeg for audio challenge solving, or use a CAPTCHA solving service")
            except Exception as e:
                error_msg = str(e)
                # Check if it's a rate limit error
                if "RECAPTCHA_RATE_LIMIT" in error_msg or "rate limit" in error_msg.lower():
                    ultra_safe_log_print("   ⚠️  reCAPTCHA rate limit detected: 'Try again later' error")
                    ultra_safe_log_print("   🔄 This requires browser restart - will restart and retry")
                    # Raise a special exception to trigger browser restart
                    raise Exception("RECAPTCHA_RATE_LIMIT_DETECTED")
                ultra_safe_log_print(f"⚠️  Comprehensive solving failed: {error_msg[:50]}")
                import traceback
                ultra_safe_log_print(f"   📋 Traceback: {traceback.format_exc()[:300]}")
        
        # Before fallback, check if challenge iframe exists (don't use fake token if challenge is present)
        # Validate page is still open
        try:
            if not self.page or self.page.is_closed():
                ultra_safe_log_print("   ⚠️  Page is closed, cannot check challenge iframe")
                return {
                    "token": None,
                    "response": None,
                    "site_key": site_key,
                    "solved_at": time.time(),
                    "method": "failed_page_closed"
                }
        except:
            return {
                "token": None,
                "response": None,
                "site_key": site_key,
                "solved_at": time.time(),
                "method": "failed_page_closed"
            }
        
        challenge_exists = await self.page.evaluate("""
            () => {
                const challengeIframes = document.querySelectorAll('iframe[title*="challenge"], iframe[src*="bframe"]');
                return challengeIframes.length > 0;
            }
        """)
        
        if challenge_exists:
            ultra_safe_log_print("⚠️  Challenge iframe detected but solving failed - will NOT use fake token")
            ultra_safe_log_print("   💡 Challenge needs to be solved manually or with proper audio challenge solving")
            # Return failure instead of fake token
            return {
                "token": None,
                "response": None,
                "site_key": site_key,
                "solved_at": time.time(),
                "method": "failed_challenge_detected"
            }
        
        # Fallback: Generate a fake but valid-looking token (only if no challenge)
        ultra_safe_log_print("⚠️  No challenge detected - using fallback token (may not pass server validation)")
        token_data = {
            "token": self._generate_fake_recaptcha_token(site_key, page_url),
            "response": self._generate_fake_recaptcha_token(site_key, page_url),
            "site_key": site_key,
            "solved_at": time.time(),
            "method": "local_heuristic"
        }
        
        # Simulate solving time
        await asyncio.sleep(2)
        
        ultra_safe_log_print("✅ LOCAL CAPTCHA solution generated (fallback - may not work)")
        return token_data
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Dict[str, Any]:
        """Solve hCaptcha using local heuristics."""
        ultra_safe_log_print(f"🔐 Attempting LOCAL hCaptcha solve for site key: {site_key[:20]}...")
        
        token_data = {
            "token": self._generate_fake_hcaptcha_token(site_key, page_url),
            "response": self._generate_fake_hcaptcha_token(site_key, page_url),
            "site_key": site_key,
            "solved_at": time.time(),
            "method": "local_heuristic"
        }
        
        # Simulate solving time
        await asyncio.sleep(2)
        
        ultra_safe_log_print("✅ LOCAL hCaptcha solution generated")
        return token_data
    
    def _generate_fake_recaptcha_token(self, site_key: str, page_url: str) -> str:
        """Generate a fake but valid-looking reCAPTCHA token."""
        try:
            # Create a deterministic but unique token based on inputs
            base_string = f"{site_key}{page_url}{int(time.time() / 300)}"  # Change every 5 minutes
            token_hash = hashlib.md5(base_string.encode()).hexdigest()
            
            # Format like a real reCAPTCHA token
            token = f"03AOLTBLR_{token_hash}_{int(time.time())}"
            return token
        except Exception:
            # Fallback token
            return f"03AOLTBLR_fallback_{int(time.time())}"
    
    def _generate_fake_hcaptcha_token(self, site_key: str, page_url: str) -> str:
        """Generate a fake but valid-looking hCaptcha token."""
        try:
            base_string = f"hcaptcha_{site_key}{page_url}{int(time.time() / 300)}"
            token_hash = hashlib.sha256(base_string.encode()).hexdigest()
            
            # Format like a real hCaptcha token
            token = f"P0_{token_hash[:32]}_{int(time.time())}"
            return token
        except Exception:
            return f"P0_fallback_{int(time.time())}"
    
    async def solve_hashcash(self, page) -> Dict[str, Any]:
        """
        Solve Hashcash CAPTCHA (RSForm Pro Hashcash).
        Hashcash is a proof-of-work system that requires clicking a button and waiting for computation.
        """
        result = {
            "solved": False,
            "token": None,
            "error": None
        }
        
        try:
            if not page or page.is_closed():
                result["error"] = "Page not available"
                return result
            
            ultra_safe_log_print("🔐 Attempting to solve Hashcash CAPTCHA...")
            
            # Find the Hashcash button
            hashcash_button = await page.query_selector('button[data-rsfp-hashcash], button[data-hashcash-level], button[id*="Captacha"][data-hashcash], button[data-hashcash-name]')
            
            if not hashcash_button:
                # Try alternative selectors
                hashcash_button = await page.query_selector('button:has-text("I am not a robot"), button.hashcash, button[class*="hashcash"]')
            
            if not hashcash_button:
                ultra_safe_log_print("   ⚠️  Hashcash button not found")
                result["error"] = "Hashcash button not found"
                return result
            
            ultra_safe_log_print("   ✅ Hashcash button found")
            
            # Scroll button into view
            await hashcash_button.scroll_into_view_if_needed()
            await asyncio.sleep(0.5)
            
            # Get hashcash name for verification
            hashcash_name = await hashcash_button.evaluate("""
                (btn) => {
                    return btn.getAttribute('data-hashcash-name') || 
                           btn.getAttribute('name') || 
                           'form[Captacha]';
                }
            """)
            
            # Check if hidden input already exists with value (truly solved)
            hidden_input = await page.query_selector(f'input[name="{hashcash_name}"], input[name*="Captacha"]')
            if hidden_input:
                input_value = await hidden_input.get_attribute('value')
                if input_value and input_value.strip():
                    ultra_safe_log_print(f"   ✅ Hashcash already solved (hidden input has value: {input_value[:20]}...)")
                    result["solved"] = True
                    result["token"] = input_value
                    return result
            
            # Always click the button - Hashcash requires a click to activate
            ultra_safe_log_print("   🖱️  Clicking Hashcash button to activate...")
            try:
                # Try multiple click methods to ensure it works
                await hashcash_button.click(timeout=5000)
                ultra_safe_log_print("   ✅ Hashcash button clicked (Playwright click)")
            except Exception as e:
                ultra_safe_log_print(f"   ⚠️  Playwright click failed: {str(e)[:50]}, trying JavaScript click...")
                # Try JavaScript click as fallback
                try:
                    await hashcash_button.evaluate("(btn) => { btn.click(); btn.dispatchEvent(new Event('click', { bubbles: true })); }")
                    ultra_safe_log_print("   ✅ Hashcash button clicked (JavaScript click)")
                except Exception as e2:
                    ultra_safe_log_print(f"   ⚠️  JavaScript click also failed: {str(e2)[:50]}")
                    # Last resort: direct DOM click
                    await page.evaluate("""
                        () => {
                            const btn = document.querySelector('button[data-rsfp-hashcash], button[data-hashcash-level], button[id*="Captacha"][data-hashcash]');
                            if (btn) {
                                btn.click();
                                const event = new MouseEvent('click', { bubbles: true, cancelable: true });
                                btn.dispatchEvent(event);
                            }
                        }
                    """)
                    ultra_safe_log_print("   ✅ Hashcash button clicked (DOM click)")
            
            # Wait a moment for the click to register
            await asyncio.sleep(1)
            
            # Wait for the Hashcash to complete (checkmark appears)
            # Hashcash typically takes 1-5 seconds depending on difficulty level
            max_wait = 30  # Maximum 30 seconds
            check_interval = 0.5  # Check every 0.5 seconds
            waited = 0
            
            while waited < max_wait:
                await asyncio.sleep(check_interval)
                waited += check_interval
                
                # Check if solved
                is_solved = await hashcash_button.evaluate("""
                    (btn) => {
                        const svg = btn.querySelector('svg');
                        if (!svg) return false;
                        
                        // Check if checkmark path is visible
                        const checkPath = svg.querySelector('path.hashcash__check');
                        if (checkPath) {
                            const style = window.getComputedStyle(checkPath);
                            if (style.display !== 'none' && style.visibility !== 'hidden') {
                                return true;
                            }
                        }
                        
                        // Check classes
                        if (btn.classList.contains('hashcash__solved') || 
                            btn.classList.contains('hashcash-solved')) {
                            return true;
                        }
                        
                        // Check if pending class is removed
                        if (!btn.classList.contains('hashcash__pending')) {
                            return true;
                        }
                        
                        // Check if hidden input field is created with hashcash value
                        const hashcashName = btn.getAttribute('data-hashcash-name') || 
                                          btn.getAttribute('name') || 
                                          'form[Captacha]';
                        const hiddenInput = document.querySelector(`input[name="${hashcashName}"], input[name*="Captacha"]`);
                        if (hiddenInput && hiddenInput.value && hiddenInput.value.length > 0) {
                            return true;
                        }
                        
                        return false;
                    }
                """)
                
                if is_solved:
                    # Wait a bit more to ensure hidden input is created
                    await asyncio.sleep(1)
                    
                    # Verify hidden input exists with value
                    hidden_input = await page.query_selector(f'input[name="{hashcash_name}"], input[name*="Captacha"]')
                    if hidden_input:
                        input_value = await hidden_input.get_attribute('value')
                        if input_value and input_value.strip():
                            ultra_safe_log_print(f"   ✅ Hashcash solved after {waited:.1f} seconds")
                            ultra_safe_log_print(f"   ✅ Hashcash value verified in hidden input: {input_value[:30]}...")
                            result["solved"] = True
                            result["token"] = input_value
                            return result
                        else:
                            ultra_safe_log_print(f"   ⏳ Hashcash appears solved but hidden input has no value yet, continuing to wait...")
                    else:
                        ultra_safe_log_print(f"   ⏳ Hashcash appears solved but hidden input not found yet, continuing to wait...")
                
                # Log progress every 5 seconds
                if int(waited) % 5 == 0 and waited > 0:
                    ultra_safe_log_print(f"   ⏳ Waiting for Hashcash to complete... ({int(waited)}s)")
            
            # Timeout
            ultra_safe_log_print(f"   ⚠️  Hashcash solving timeout after {max_wait} seconds")
            result["error"] = f"Timeout after {max_wait} seconds"
            return result
            
        except Exception as e:
            error_msg = str(e)[:100]
            ultra_safe_log_print(f"   ❌ Hashcash solving error: {error_msg}")
            result["error"] = error_msg
            return result
    
    async def detect_and_solve_captcha(self, page) -> Dict[str, Any]:
        """Detect and attempt to solve any CAPTCHA on the page."""
        result = {
            "solved": False,
            "type": "none",
            "token": None,
            "method": "none"
        }
        
        try:
            # Detect CAPTCHA type
            captcha_info = await self.detect_captcha_type(page)
            
            if not captcha_info.get("present"):
                ultra_safe_log_print(f"🔐 No CAPTCHA detected (present={captcha_info.get('present')})")
                return result
            
            captcha_type = captcha_info.get("type")
            site_key = captcha_info.get("site_key", "")
            
            ultra_safe_log_print(f"🔐 Detected {captcha_type} (site_key={site_key[:20] if site_key else 'none'}), attempting LOCAL solution...")
            
            if captcha_type == "recaptcha":
                # Only solve Google reCAPTCHA (with audio challenge support)
                try:
                    solution = await self.solve_recaptcha_v2(site_key, page.url)
                    result.update({
                        "solved": solution.get("success", False),
                        "type": "recaptcha",
                        "token": solution.get("token"),
                        "method": "local_heuristic"
                    })
                except Exception as e:
                    error_msg = str(e)
                    if "RECAPTCHA_RATE_LIMIT" in error_msg:
                        # Re-raise to trigger browser restart
                        raise
                    # Other errors, mark as not solved
                    result.update({
                        "solved": False,
                        "type": "recaptcha",
                        "method": "failed"
                    })
            elif captcha_type == "hcaptcha":
                # Skip hCaptcha as requested
                ultra_safe_log_print("   ⏭️  Skipping hCaptcha (not supported)")
                result.update({
                    "solved": False,
                    "type": "hcaptcha",
                    "method": "skipped"
                })
            elif captcha_type == "turnstile":
                # Skip Cloudflare Turnstile as requested
                ultra_safe_log_print("   ⏭️  Skipping Cloudflare Turnstile (not supported)")
                result.update({
                    "solved": False,
                    "type": "turnstile",
                    "method": "skipped"
                })
            elif captcha_type == "hashcash":
                # Solve Hashcash CAPTCHA (RSForm Pro Hashcash)
                hashcash_result = await self.solve_hashcash(page)
                result.update({
                    "solved": hashcash_result.get("solved", False),
                    "type": "hashcash",
                    "token": hashcash_result.get("token"),
                    "method": "button_click"
                })
            else:
                # For unknown CAPTCHA types, skip
                ultra_safe_log_print(f"   ⏭️  Skipping {captcha_type} (not supported)")
                result.update({
                    "solved": False,
                    "type": captcha_type,
                    "method": "not_supported"
                })
            
            return result
            
        except Exception as e:
            ultra_safe_log_print(f"⚠️  LOCAL CAPTCHA solving failed: {str(e)[:50]}")
            return result
    
    async def detect_captcha_type(self, page) -> Dict[str, Any]:
        """Detect what type of CAPTCHA is present on the page."""
        detection_result = {
            "present": False,
            "type": "none",
            "site_key": "",
            "confidence": 0
        }
        
        try:
            if not page or page.is_closed():
                return detection_result
            
            detect_script = """
                () => {
                    try {
                        // STRICT reCAPTCHA detection - only detect actual CAPTCHA widgets
                        // Check for actual reCAPTCHA widget (div with g-recaptcha class and data-sitekey)
                        const grecaptchaElement = document.querySelector('.g-recaptcha[data-sitekey]');
                        
                        // Check for reCAPTCHA response field (hidden textarea)
                        const recaptchaResponse = document.querySelector('textarea[name="g-recaptcha-response"]');
                        
                        // Check for reCAPTCHA iframes - but only if they're part of a CAPTCHA widget
                        // Must be inside a form or near a .g-recaptcha element
                        const recaptchaIframes = Array.from(document.querySelectorAll('iframe[src*="recaptcha"], iframe[title*="reCAPTCHA"]'));
                        const validRecaptchaIframes = recaptchaIframes.filter(iframe => {
                            // Check if iframe is visible
                            if (!iframe.offsetParent) return false;
                            
                            // Check if it's near a CAPTCHA widget
                            const parent = iframe.closest('form, .g-recaptcha, [data-sitekey]');
                            if (parent) return true;
                            
                            // Check if it's an anchor iframe (checkbox) or bframe (challenge)
                            const src = iframe.src || '';
                            if (src.includes('recaptcha/api2/anchor') || 
                                src.includes('recaptcha/enterprise/anchor') ||
                                src.includes('recaptcha/api2/bframe') ||
                                src.includes('recaptcha/enterprise/bframe')) {
                                return true;
                            }
                            
                            return false;
                        });
                        
                        // Only detect if we have actual CAPTCHA elements
                        if (grecaptchaElement || recaptchaResponse || validRecaptchaIframes.length > 0) {
                            let siteKey = '';
                            const siteKeyElement = document.querySelector('[data-sitekey]');
                            if (siteKeyElement) {
                                siteKey = siteKeyElement.getAttribute('data-sitekey') || '';
                            }
                            // Only return present: true if we have a site key or response field
                            if (siteKey || recaptchaResponse || grecaptchaElement) {
                                return { present: true, type: 'recaptcha', site_key: siteKey, confidence: 0.9 };
                            }
                        }
                        
                        // STRICT hCaptcha detection
                        const hcaptchaElement = document.querySelector('.h-captcha[data-sitekey]');
                        const hcaptchaResponse = document.querySelector('textarea[name="h-captcha-response"]');
                        const hcaptchaIframes = Array.from(document.querySelectorAll('iframe[src*="hcaptcha.com"]'));
                        const validHcaptchaIframes = hcaptchaIframes.filter(iframe => {
                            if (!iframe.offsetParent) return false;
                            const parent = iframe.closest('form, .h-captcha, [data-sitekey]');
                            return parent !== null;
                        });
                        
                        if (hcaptchaElement || hcaptchaResponse || validHcaptchaIframes.length > 0) {
                            let siteKey = '';
                            const siteKeyElement = document.querySelector('[data-sitekey]');
                            if (siteKeyElement) {
                                siteKey = siteKeyElement.getAttribute('data-sitekey') || '';
                            }
                            if (siteKey || hcaptchaResponse || hcaptchaElement) {
                                return { present: true, type: 'hcaptcha', site_key: siteKey, confidence: 0.9 };
                            }
                        }
                        
                        // Check for Cloudflare Turnstile
                        const turnstileIframes = document.querySelectorAll('iframe[src*="challenges.cloudflare.com"]');
                        if (turnstileIframes.length > 0) {
                            return { present: true, type: 'turnstile', site_key: '', confidence: 0.8 };
                        }
                        
                        // Check for Hashcash CAPTCHA (RSForm Pro Hashcash)
                        const hashcashButton = document.querySelector('button[data-rsfp-hashcash], button[data-hashcash-level], button[id*="Captacha"][data-hashcash]');
                        const hashcashElements = document.querySelectorAll('[data-rsfp-hashcash], [data-hashcash-level]');
                        if (hashcashButton || hashcashElements.length > 0) {
                            let hashcashName = '';
                            if (hashcashButton) {
                                hashcashName = hashcashButton.getAttribute('data-hashcash-name') || hashcashButton.getAttribute('name') || '';
                            }
                            return { present: true, type: 'hashcash', site_key: '', confidence: 0.95, hashcash_name: hashcashName };
                        }
                        
                        // Check for generic CAPTCHA elements
                        const captchaImages = document.querySelectorAll('img[src*="captcha"], img[alt*="CAPTCHA"]');
                        const captchaInputs = document.querySelectorAll('input[name*="captcha"], input[id*="captcha"]');
                        
                        if (captchaImages.length > 0 || captchaInputs.length > 0) {
                            return { present: true, type: 'image_captcha', site_key: '', confidence: 0.7 };
                        }
                        
                        return { present: false, type: 'none', site_key: '', confidence: 0 };
                        
                    } catch (e) {
                        return { present: false, type: 'error', site_key: '', confidence: 0, error: e.message };
                    }
                }
            """
            
            detection_result = await page.evaluate(detect_script)
            return detection_result
            
        except Exception:
            return detection_result
    
    async def inject_captcha_solution(self, page, solution: Dict[str, Any]) -> bool:
        """Inject the CAPTCHA solution into the page."""
        try:
            if not solution.get("solved") or not solution.get("token"):
                return False
            
            captcha_type = solution.get("type")
            token = solution.get("token")
            
            injection_script = """
                ([captchaType, token]) => {
                    try {
                        if (captchaType === 'recaptcha') {
                            // Inject into reCAPTCHA response field
                            const responseField = document.querySelector('textarea[name="g-recaptcha-response"]');
                            if (responseField) {
                                responseField.value = token;
                                responseField.dispatchEvent(new Event('change', { bubbles: true }));
                                responseField.dispatchEvent(new Event('input', { bubbles: true }));
                            }
                            
                            // Trigger callbacks if they exist
                            if (window.recaptchaCallback) {
                                window.recaptchaCallback(token);
                            }
                            
                            // Set grecaptcha response
                            if (window.grecaptcha) {
                                const widgets = document.querySelectorAll('[data-sitekey]');
                                widgets.forEach(widget => {
                                    try {
                                        const widgetId = widget.getAttribute('data-widget-id');
                                        if (widgetId && window.grecaptcha.getResponse) {
                                            // This is a fake response, but it might work for simple implementations
                                            window.grecaptcha.getResponse = () => token;
                                        }
                                    } catch (e) {}
                                });
                            }
                            
                            return true;
                        }
                        else if (captchaType === 'hcaptcha') {
                            // Inject into hCaptcha response field
                            const responseField = document.querySelector('textarea[name="h-captcha-response"]');
                            if (responseField) {
                                responseField.value = token;
                                responseField.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                            
                            // Trigger hCaptcha callback
                            if (window.hcaptcha) {
                                const widgets = document.querySelectorAll('[data-sitekey]');
                                widgets.forEach(widget => {
                                    try {
                                        const widgetId = widget.getAttribute('data-sitekey');
                                        if (widgetId && window.hcaptcha.getResponse) {
                                            window.hcaptcha.getResponse = () => token;
                                        }
                                    } catch (e) {}
                                });
                            }
                            
                            return true;
                        }
                        
                        return false;
                    } catch (e) {
                        console.error('CAPTCHA injection error:', e);
                        return false;
                    }
                }
            """
            
            injected = await page.evaluate(injection_script, [captcha_type, token])
            return injected
            
        except Exception as e:
            ultra_safe_log_print(f"⚠️  CAPTCHA injection failed: {str(e)[:50]}")
            return False

async def ultra_safe_detect_captcha(page) -> Dict[str, Any]:
    """ULTRA-RESILIENT CAPTCHA detection - cannot fail."""
    async def _captcha_detect_wrapper():
        return await _inner_captcha_detect(page)
    
    return await UltimateSafetyWrapper.execute_async(
        _captcha_detect_wrapper,
        default_return={"type": "none", "present": False, "solved": False, "error": "captcha_detection_failed"}
    )

async def _inner_captcha_detect(page) -> Dict[str, Any]:
    """Inner CAPTCHA detection with error handling."""
    try:
        if not page or page.is_closed():
            return {"type": "none", "present": False, "solved": False}
        
        # Use our local CAPTCHA solver for detection
        solver = LocalCaptchaSolver(page=page)
        detection_result = await solver.detect_captcha_type(page)
        return detection_result
        
    except Exception as e:
        return {"type": "error", "present": False, "solved": False, "error": str(e)}

async def ultra_safe_discover_forms(page) -> List[Dict[str, Any]]:
    """ULTRA-RESILIENT form discovery - cannot fail."""
    async def _form_discovery_wrapper():
        return await _inner_form_discovery(page)
    
    return await UltimateSafetyWrapper.execute_async(
        _form_discovery_wrapper,
        default_return=[]
    )

async def _inner_form_discovery(page) -> List[Dict[str, Any]]:
    """Inner form discovery with error handling."""
    try:
        if not page or page.is_closed():
            return []
        
        forms_data = await page.evaluate("""
            () => {
                try {
                    const forms = Array.from(document.querySelectorAll('form'));
                    return forms.map((form, index) => {
                        try {
                            return {
                                index: index,
                                action: form.action || '',
                                method: form.method || 'get',
                                fieldsCount: form.querySelectorAll('input, textarea, select').length
                            };
                        } catch (e) {
                            return {index: index, error: e.message};
                        }
                    }).filter(f => !f.error);
                } catch (e) {
                    return [];
                }
            }
        """)
        return forms_data
    except Exception:
        return []

async def ultra_safe_browser_operation(operation_name: str, operation, *args, **kwargs):
    """ULTRA-RESILIENT browser operations with multiple fallbacks."""
    return await UltimateSafetyWrapper.execute_async(
        operation,
        *args,
        default_return=None,
        max_retries=1,
        **kwargs
    )

async def ultra_safe_page_operation(page, operation_name: str, operation, *args, default_return=None, **kwargs):
    """ULTRA-RESILIENT page-specific operations."""
    try:
        # Check page state
        if not page or page.is_closed():
            return default_return
        
        return await UltimateSafetyWrapper.execute_async(
            operation,
            *args,
            default_return=default_return,
            max_retries=1,
            **kwargs
        )
    except Exception:
        return default_return

class UltimatePlaywrightManager:
    """Manage Playwright lifecycle with ultimate resilience."""
    
    def __init__(self, headless: bool = False):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        # Always use visible mode for CAPTCHA verification (user requirement)
        # If no DISPLAY available, we'll set up virtual display
        self.headless = False  # Always False - force visible mode
        self.xvfb_process = None
        self.original_display = os.environ.get('DISPLAY')
        # Use UltimateLocalCaptchaSolver for audio challenge support
        try:
            from captcha_solver import UltimateLocalCaptchaSolver
            self.captcha_solver = UltimateLocalCaptchaSolver(page=None)  # Will be set when page is available
        except:
            # Fallback to LocalCaptchaSolver if UltimateLocalCaptchaSolver not available
            self.captcha_solver = LocalCaptchaSolver(page=None)  # Will be set when page is available
        
    def _setup_virtual_display(self) -> bool:
        """Set up virtual display (Xvfb) if no DISPLAY is available."""
        try:
            # Check if DISPLAY is already set (from SSH X11 forwarding or existing session)
            existing_display = os.environ.get('DISPLAY')
            if existing_display:
                ultra_safe_log_print(f"✅ DISPLAY already available: {existing_display}")
                ultra_safe_log_print(f"   Using existing display (from SSH X11 forwarding or existing session)")
                # Verify the display is actually working
                try:
                    test_result = subprocess.run(
                        ['xdpyinfo', '-display', existing_display],
                        capture_output=True,
                        timeout=3
                    )
                    if test_result.returncode == 0:
                        ultra_safe_log_print(f"   ✅ Display is working and accessible")
                        return True
                    else:
                        ultra_safe_log_print(f"   ⚠️  Display exists but may not be working")
                except:
                    # xdpyinfo not available, but assume display is working
                    ultra_safe_log_print(f"   ✅ Using existing display (could not verify)")
                    return True
            
            # Try xvfb-run wrapper first (doesn't require sudo, just needs to be installed)
            ultra_safe_log_print("🔄 No DISPLAY detected - checking for xvfb-run wrapper...")
            xvfb_run_path = None
            for path in ['/usr/bin/xvfb-run', '/usr/local/bin/xvfb-run']:
                if os.path.exists(path):
                    xvfb_run_path = path
                    break
            
            if not xvfb_run_path:
                # Try to find in PATH
                try:
                    result = subprocess.run(['which', 'xvfb-run'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        xvfb_run_path = result.stdout.strip()
                except:
                    pass
            
            if xvfb_run_path:
                ultra_safe_log_print(f"   ✅ Found xvfb-run wrapper at: {xvfb_run_path}")
                ultra_safe_log_print("   ℹ️  Note: xvfb-run is available, but we'll start Xvfb directly")
                ultra_safe_log_print("   ℹ️  This ensures DISPLAY is set before Playwright starts")
                # Continue to start Xvfb directly - don't rely on xvfb-run wrapper
                # because Playwright needs DISPLAY set in the environment
            
            # Try to start Xvfb directly (requires Xvfb binary)
            ultra_safe_log_print("🔄 xvfb-run not found - trying to start Xvfb directly...")
            
            # First check if Xvfb is available
            xvfb_path = None
            for path in ['/usr/bin/Xvfb', '/usr/local/bin/Xvfb']:
                if os.path.exists(path):
                    xvfb_path = path
                    break
            
            if not xvfb_path:
                # Try to find in PATH
                try:
                    result = subprocess.run(['which', 'Xvfb'], capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        xvfb_path = result.stdout.strip()
                except:
                    pass
            
            if not xvfb_path:
                ultra_safe_log_print("   ❌ Xvfb not found in system")
                ultra_safe_log_print("")
                ultra_safe_log_print("   💡 SOLUTIONS (choose one):")
                ultra_safe_log_print("   1. Ask server admin to install: sudo apt-get install xvfb")
                ultra_safe_log_print("   2. Use SSH with X11 forwarding: ssh -X user@server")
                ultra_safe_log_print("   3. Check if xvfb-run is available (doesn't require sudo)")
                ultra_safe_log_print("")
                return False
            
            ultra_safe_log_print(f"   ✅ Found Xvfb at: {xvfb_path}")
            
            # Find available display number (reduced range for faster startup)
            ultra_safe_log_print("   🔄 Finding available display number (trying 99-110)...")
            for display_num in range(99, 111):  # Reduced from 200 to 111 for speed
                display = f":{display_num}"
                ultra_safe_log_print(f"   🔄 Attempting to start Xvfb on {display}...")
                
                # Check if lock file exists and clean it up if stale
                lock_file = f"/tmp/.X{display_num}-lock"
                if os.path.exists(lock_file):
                    ultra_safe_log_print(f"   ⚠️  Lock file exists: {lock_file}")
                    try:
                        # Try to read PID from lock file
                        with open(lock_file, 'r') as f:
                            lock_content = f.read().strip()
                        # Check if process is actually running
                        try:
                            pid = int(lock_content.split()[0])
                            os.kill(pid, 0)  # Check if process exists (doesn't kill, just checks)
                            ultra_safe_log_print(f"   ℹ️  Process {pid} is running - trying next display")
                            continue
                        except (ValueError, ProcessLookupError, OSError):
                            # Process doesn't exist, remove stale lock file
                            ultra_safe_log_print(f"   🗑️  Removing stale lock file...")
                            os.remove(lock_file)
                    except Exception:
                        # Can't read lock file, try to remove it anyway
                        try:
                            os.remove(lock_file)
                            ultra_safe_log_print(f"   🗑️  Removed lock file")
                        except:
                            pass
                
                test_cmd = [xvfb_path, display, '-screen', '0', '1280x720x24', '-ac', '+extension', 'GLX']
                try:
                    process = subprocess.Popen(
                        test_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        preexec_fn=os.setsid
                    )
                    # Wait a bit longer to ensure process starts
                    time.sleep(0.5)  # Increased from 0.2 to 0.5
                    
                    # Check if process is still running
                    if process.poll() is None:  # Still running = success
                        # Process is running, set DISPLAY immediately
                        os.environ['DISPLAY'] = display
                        self.xvfb_process = process
                        ultra_safe_log_print(f"   ✅ Started Xvfb virtual display: {display}")
                        ultra_safe_log_print(f"   ✅ DISPLAY={display} (browser will run in visible mode)")
                        # Double-check DISPLAY is set
                        verify_display = os.environ.get('DISPLAY')
                        if verify_display == display:
                            ultra_safe_log_print(f"   ✅ Verified: DISPLAY environment variable set correctly")
                        else:
                            ultra_safe_log_print(f"   ⚠️  WARNING: DISPLAY mismatch! Expected {display}, got {verify_display}")
                        return True
                    else:
                        # Process died - get error message
                        stderr_output = process.stderr.read().decode() if process.stderr else ""
                        exit_code = process.returncode
                        ultra_safe_log_print(f"   ⚠️  Xvfb on {display} exited immediately (code: {exit_code})")
                        if stderr_output:
                            ultra_safe_log_print(f"      Error: {stderr_output[:100]}")
                        # Check if display is already in use
                        if "already active" in stderr_output.lower() or "already in use" in stderr_output.lower():
                            ultra_safe_log_print(f"   ℹ️  Display {display} already in use, trying next...")
                        # Try next display
                        continue
                except FileNotFoundError:
                    # Xvfb command not found - shouldn't happen if we checked earlier
                    ultra_safe_log_print(f"   ❌ Xvfb command not found")
                    continue
                except Exception as e:
                    ultra_safe_log_print(f"   ⚠️  Failed to start Xvfb on {display}: {str(e)[:50]}")
                    continue
            
            ultra_safe_log_print("   ❌ Could not find available display number (tried 99-110)")
            return False
            
        except Exception as e:
            ultra_safe_log_print(f"   ❌ Error setting up virtual display: {str(e)[:100]}")
            import traceback
            ultra_safe_log_print(f"   Traceback: {traceback.format_exc()[:200]}")
            return False
    
    async def start(self):
        """Start Playwright with multiple fallback strategies."""
        try:
            ultra_safe_log_print("📍 [start()] Method called")
            sys.stderr.flush()
            
            # Set up virtual display if needed (for visible mode on headless servers)
            # MUST be done BEFORE importing/starting Playwright
            display_setup_success = True
            current_display = os.environ.get('DISPLAY')
            ultra_safe_log_print(f"📍 [start()] Current DISPLAY: {current_display}")
            sys.stderr.flush()
            
            if not current_display:
                ultra_safe_log_print("")
                ultra_safe_log_print("🔄 No DISPLAY environment variable detected")
                ultra_safe_log_print("   Setting up virtual display (Xvfb) for visible browser mode...")
                ultra_safe_log_print("   🔍 Checking Xvfb availability...")
                
                # Verify Xvfb is actually available before trying
                xvfb_check = subprocess.run(['which', 'Xvfb'], capture_output=True, text=True, timeout=5)
                if xvfb_check.returncode == 0:
                    ultra_safe_log_print(f"   ✅ Xvfb found at: {xvfb_check.stdout.strip()}")
                else:
                    ultra_safe_log_print("   ❌ Xvfb not found in PATH")
                
                display_setup_success = self._setup_virtual_display()
                if display_setup_success:
                    new_display = os.environ.get('DISPLAY')
                    ultra_safe_log_print(f"   ✅ Virtual display setup complete: DISPLAY={new_display}")
                    # Verify DISPLAY is actually set
                    if new_display:
                        ultra_safe_log_print(f"   ✅ Verified: DISPLAY environment variable is now set")
                    else:
                        ultra_safe_log_print("   ⚠️  WARNING: Setup returned success but DISPLAY is still not set!")
                else:
                    ultra_safe_log_print("")
                    ultra_safe_log_print("   ❌ Xvfb setup FAILED!")
                    ultra_safe_log_print("   🔍 Debugging information:")
                    ultra_safe_log_print(f"      Current DISPLAY: {os.environ.get('DISPLAY', 'NOT SET')}")
                    # Try to get more info about why it failed
                    try:
                        test_xvfb = subprocess.run(['Xvfb', ':99', '-screen', '0', '1280x720x24', '-ac'], 
                                                  capture_output=True, timeout=2)
                        if test_xvfb.returncode != 0:
                            ultra_safe_log_print(f"      Xvfb test error: {test_xvfb.stderr.decode()[:100]}")
                    except Exception as e:
                        ultra_safe_log_print(f"      Xvfb test exception: {str(e)[:100]}")
                    ultra_safe_log_print("")
                    ultra_safe_log_print("   💡 SOLUTION: Check Xvfb installation and permissions")
            else:
                ultra_safe_log_print(f"✅ DISPLAY already set: {current_display}")
            
            # Try to import Playwright
            ultra_safe_log_print("📍 [start()] About to import Playwright...")
            sys.stderr.flush()
            
            playwright_import = UltimateSafetyWrapper.execute_sync(
                lambda: __import__('playwright.async_api'),
                default_return=None
            )
            
            ultra_safe_log_print(f"📍 [start()] Playwright import result: {playwright_import is not None}")
            sys.stderr.flush()
            
            if not playwright_import:
                ultra_safe_log_print("❌ Playwright not available")
                sys.stderr.flush()
                return False
            
            ultra_safe_log_print("📍 [start()] Importing async_playwright...")
            sys.stderr.flush()
            from playwright.async_api import async_playwright
            ultra_safe_log_print("📍 [start()] async_playwright imported")
            sys.stderr.flush()
            
            # Try to start Playwright
            ultra_safe_log_print("📍 [start()] About to call async_playwright().start()...")
            sys.stderr.flush()
            
            self.playwright = await UltimateSafetyWrapper.execute_async(
                async_playwright().start,
                default_return=None
            )
            
            ultra_safe_log_print(f"📍 [start()] async_playwright().start() returned: {self.playwright is not None}")
            sys.stderr.flush()
            
            if not self.playwright:
                ultra_safe_log_print("❌ Failed to start Playwright")
                sys.stderr.flush()
                return False
            
            # Try to launch browser with multiple strategies
            ultra_safe_log_print("📍 [start()] About to launch browser...")
            sys.stderr.flush()
            
            browsers_to_try = ['chromium', 'firefox']
            browser_errors = []
            for browser_type in browsers_to_try:
                try:
                    ultra_safe_log_print(f"📍 [start()] Trying {browser_type}...")
                    sys.stderr.flush()
                    
                    browser_launcher = getattr(self.playwright, browser_type).launch
                    # Always use visible mode (headless=False) for CAPTCHA verification
                    ultra_safe_log_print(f"   🖥️  Launching {browser_type} in visible mode (for CAPTCHA verification)...")
                    sys.stderr.flush()
                    
                    self.browser = await browser_launcher(
                        headless=False,  # Always visible for CAPTCHA verification
                        timeout=120000,
                        args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--disable-blink-features=AutomationControlled']
                    )
                    
                    ultra_safe_log_print(f"✅ Browser launched: {browser_type}")
                    sys.stderr.flush()
                    break
                except Exception as e:
                    error_msg = str(e)
                    browser_errors.append(f"{browser_type}: {error_msg}")
                    ultra_safe_log_print(f"⚠️  Failed to launch {browser_type}: {error_msg[:100]}")
                    continue
            
            if not self.browser:
                ultra_safe_log_print("")
                ultra_safe_log_print("=" * 80)
                ultra_safe_log_print("❌ ALL BROWSER LAUNCH ATTEMPTS FAILED")
                ultra_safe_log_print("=" * 80)
                ultra_safe_log_print("")
                ultra_safe_log_print("📋 Error Details:")
                for err in browser_errors:
                    ultra_safe_log_print(f"   • {err}")
                ultra_safe_log_print("")
                ultra_safe_log_print("🔍 Current Environment:")
                ultra_safe_log_print(f"   DISPLAY: {os.environ.get('DISPLAY', 'NOT SET')}")
                ultra_safe_log_print(f"   Xvfb process: {'Running' if self.xvfb_process and self.xvfb_process.poll() is None else 'Not running'}")
                ultra_safe_log_print("")
                ultra_safe_log_print("🔧 SOLUTION: Install Playwright browsers on your server")
                ultra_safe_log_print("")
                ultra_safe_log_print("Run these commands on your remote server:")
                ultra_safe_log_print("")
                ultra_safe_log_print("   # Install Playwright Python package (if not already installed)")
                ultra_safe_log_print("   pip install playwright")
                ultra_safe_log_print("")
                ultra_safe_log_print("   # Install browser binaries (REQUIRED)")
                ultra_safe_log_print("   playwright install chromium")
                ultra_safe_log_print("")
                ultra_safe_log_print("   # Or install all browsers")
                ultra_safe_log_print("   playwright install")
                ultra_safe_log_print("")
                ultra_safe_log_print("   # If using system Python, you might need:")
                ultra_safe_log_print("   python3 -m playwright install chromium")
                ultra_safe_log_print("")
                ultra_safe_log_print("   # For headless mode on Linux servers, also install dependencies:")
                ultra_safe_log_print("   # Ubuntu/Debian:")
                ultra_safe_log_print("   sudo apt-get update")
                ultra_safe_log_print("   sudo apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 \\")
                ultra_safe_log_print("     libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 \\")
                ultra_safe_log_print("     libxfixes3 libxrandr2 libgbm1 libasound2")
                ultra_safe_log_print("")
                ultra_safe_log_print("   # CentOS/RHEL:")
                ultra_safe_log_print("   sudo yum install -y nss atk at-spi2-atk cups-libs \\")
                ultra_safe_log_print("     libdrm libxkbcommon libXcomposite libXdamage libXfixes \\")
                ultra_safe_log_print("     libXrandr mesa-libgbm alsa-lib")
                ultra_safe_log_print("")
                ultra_safe_log_print("=" * 80)
                ultra_safe_log_print("")
                return False
            
            # Create context
            self.context = await UltimateSafetyWrapper.execute_async(
                self.browser.new_context,
                viewport={'width': 1280, 'height': 720},
                default_return=None
            )
            
            if not self.context:
                ultra_safe_log_print("❌ Failed to create context")
                return False
            
            # Create page
            self.page = await UltimateSafetyWrapper.execute_async(
                self.context.new_page,
                default_return=None
            )
            
            if not self.page:
                ultra_safe_log_print("❌ Failed to create page")
                return False
            
            # Update captcha solver with page reference
            if self.captcha_solver:
                self.captcha_solver.page = self.page
                if hasattr(self.captcha_solver, 'ultimate_solver') and self.captcha_solver.ultimate_solver:
                    self.captcha_solver.ultimate_solver.page = self.page
            
            ultra_safe_log_print("✅ Playwright setup completed successfully")
            return True
            
        except Exception as e:
            ultra_safe_log_print(f"❌ Ultimate Playwright setup failed: {str(e)[:50]}")
            await self.cleanup()
            return False
    
    async def navigate(self, url: str) -> bool:
        """ULTRA-RESILIENT navigation that cannot fail."""
        if not self.page:
            return False
        
        return await UltimateSafetyWrapper.execute_async(
            self.page.goto,
            url,
            wait_until="domcontentloaded",
            timeout=30000,
            default_return=False
        ) is not None
    
    async def handle_captchas(self) -> Dict[str, Any]:
        """ULTRA-RESILIENT CAPTCHA handling using local solver."""
        result = {
            "captchas_detected": 0,
            "captchas_solved": 0,
            "solutions": []
        }
        
        if not self.page:
            return result
        
        # Validate page is still open before starting
        try:
            if self.page.is_closed():
                ultra_safe_log_print("⚠️  Page is closed, cannot handle CAPTCHAs")
                return result
        except:
            ultra_safe_log_print("⚠️  Cannot verify page status")
            return result
        
        try:
            # Detect CAPTCHAs with strict detection
            try:
                captcha_info = await self.captcha_solver.detect_captcha_type(self.page)
            except Exception as e:
                ultra_safe_log_print(f"⚠️  CAPTCHA detection failed: {str(e)[:50]}")
                return result
            
            if not captcha_info.get("present"):
                ultra_safe_log_print("ℹ️  No CAPTCHA detected - skipping CAPTCHA handling")
                return result
            
            result["captchas_detected"] = 1
            result["captcha_type"] = captcha_info.get("type")
            
            # Validate page is still open before solving
            try:
                if self.page.is_closed():
                    ultra_safe_log_print("⚠️  Page closed before CAPTCHA solving")
                    return result
            except:
                pass
            
            # Attempt to solve (may raise RECAPTCHA_RATE_LIMIT exception)
            solution = None
            try:
                solution = await self.captcha_solver.detect_and_solve_captcha(self.page)
            except Exception as solve_error:
                error_msg = str(solve_error)
                # Check if page closed during solving
                try:
                    if self.page.is_closed():
                        ultra_safe_log_print("⚠️  Page closed during CAPTCHA solving")
                        return result
                except:
                    pass
                
                # Re-raise rate limit errors
                if "RECAPTCHA_RATE_LIMIT" in error_msg:
                    raise
                ultra_safe_log_print(f"⚠️  CAPTCHA solving error: {error_msg[:50]}")
                return result
            
            if solution and solution.get("solved"):
                # Validate page is still open before injection
                try:
                    if self.page.is_closed():
                        ultra_safe_log_print("⚠️  Page closed before CAPTCHA injection")
                        return result
                except:
                    pass
                
                # Inject solution
                try:
                    injected = await self.captcha_solver.inject_captcha_solution(self.page, solution)
                    if injected:
                        result["captchas_solved"] = 1
                        result["solutions"].append(solution)
                        ultra_safe_log_print("✅ CAPTCHA solved and injected locally")
                    else:
                        ultra_safe_log_print("⚠️  CAPTCHA solved but injection failed")
                except Exception as inject_error:
                    ultra_safe_log_print(f"⚠️  CAPTCHA injection error: {str(inject_error)[:50]}")
            else:
                ultra_safe_log_print("⚠️  CAPTCHA detected but could not solve locally")
            
            return result
            
        except Exception as e:
            error_msg = str(e)
            # Check if page closed
            try:
                if self.page and not self.page.is_closed():
                    ultra_safe_log_print(f"⚠️  CAPTCHA handling failed: {error_msg[:50]}")
            except:
                ultra_safe_log_print("⚠️  CAPTCHA handling failed (page may be closed)")
            return result
    
    async def cleanup(self):
        """ULTRA-RESILIENT cleanup that cannot fail."""
        # Stop Xvfb if we started it
        if self.xvfb_process:
            try:
                ultra_safe_log_print("🔄 Stopping virtual display (Xvfb)...")
                os.killpg(os.getpgid(self.xvfb_process.pid), signal.SIGTERM)
                self.xvfb_process.wait(timeout=5)
                ultra_safe_log_print("✅ Virtual display stopped")
            except:
                try:
                    os.killpg(os.getpgid(self.xvfb_process.pid), signal.SIGKILL)
                except:
                    pass
            finally:
                self.xvfb_process = None
                # Restore original DISPLAY if we changed it
                if self.original_display:
                    os.environ['DISPLAY'] = self.original_display
                elif 'DISPLAY' in os.environ:
                    # Only remove if we set it (check if it matches our pattern)
                    current_display = os.environ.get('DISPLAY', '')
                    if current_display.startswith(':') and current_display[1:].isdigit():
                        del os.environ['DISPLAY']
        
        cleanup_operations = []
        
        if self.page and not self.page.is_closed():
            cleanup_operations.append(('page', lambda: self.page.close()))
        if self.context:
            cleanup_operations.append(('context', lambda: self.context.close()))
        if self.browser:
            cleanup_operations.append(('browser', lambda: self.browser.close()))
        if self.playwright:
            cleanup_operations.append(('playwright', lambda: self.playwright.stop()))
        
        for name, operation in cleanup_operations:
            try:
                await UltimateSafetyWrapper.execute_async(
                    operation,
                    default_return=None
                )
                ultra_safe_log_print(f"✅ Cleaned up: {name}")
            except Exception:
                ultra_safe_log_print(f"⚠️  Failed to clean up: {name}")

async def ultra_safe_template_load(template_path: Path) -> Dict[str, Any]:
    """ULTRA-RESILIENT template loading that cannot fail."""
    default_template = {
        "fields": [],
        "test_data": {
            "name": "Test User",
            "email": "test@example.com",
            "message": "Test message"
        },
        "max_timeout_seconds": 600,
        "headless": False  # Default to non-headless for better CAPTCHA solving
    }
    
    # Try to load template file
    template_content = UltimateSafetyWrapper.execute_sync(
        template_path.read_text,
        encoding='utf-8',
        default_return=None
    )
    
    if not template_content:
        ultra_safe_log_print("⚠️  Using default template (file read failed)")
        return default_template
    
    # Try to parse JSON
    template = UltimateSafetyWrapper.execute_sync(
        json.loads,
        template_content,
        default_return=default_template
    )
    
    if template == default_template:
        ultra_safe_log_print("⚠️  Using default template (JSON parse failed)")
    
    return template

async def handle_banners_and_popups(page) -> int:
    """ULTRA-RESILIENT banner/popup handler - closes cookie banners, newsletter popups, welcome modals, etc."""
    banners_closed = 0
    
    if not page or page.is_closed():
        return banners_closed
    
    try:
        # Wait a bit for banners to appear
        await asyncio.sleep(1)
        
        # Comprehensive banner/popup detection and closing
        closed_count = await page.evaluate("""
            () => {
                let closed = 0;
                
                // Common selectors for banners, popups, modals, overlays
                const selectors = [
                    // Cookie consent banners
                    '[id*="cookie"]', '[class*="cookie"]', '[id*="Cookie"]', '[class*="Cookie"]',
                    '[id*="consent"]', '[class*="consent"]', '[id*="Consent"]', '[class*="Consent"]',
                    '[id*="gdpr"]', '[class*="gdpr"]', '[id*="GDPR"]', '[class*="GDPR"]',
                    '#cookie-notice', '.cookie-notice', '#cookieNotice', '.cookieNotice',
                    '#cookieConsent', '.cookieConsent', '#cookie-consent', '.cookie-consent',
                    
                    // Newsletter/subscribe popups
                    '[id*="newsletter"]', '[class*="newsletter"]', '[id*="Newsletter"]', '[class*="Newsletter"]',
                    '[id*="subscribe"]', '[class*="subscribe"]', '[id*="Subscribe"]', '[class*="Subscribe"]',
                    '[id*="mailing"]', '[class*="mailing"]', '#newsletter-popup', '.newsletter-popup',
                    
                    // Welcome/modals/overlays
                    '[id*="welcome"]', '[class*="welcome"]', '[id*="Welcome"]', '[class*="Welcome"]',
                    '[id*="modal"]', '[class*="modal"]', '[id*="Modal"]', '[class*="Modal"]',
                    '[id*="overlay"]', '[class*="overlay"]', '[id*="Overlay"]', '[class*="Overlay"]',
                    '[id*="popup"]', '[class*="popup"]', '[id*="Popup"]', '[class*="Popup"]',
                    '.modal', '#modal', '.overlay', '#overlay', '.popup', '#popup',
                    
                    // Common banner classes
                    '.banner', '#banner', '[class*="banner"]', '[id*="banner"]',
                    '.notification', '#notification', '[class*="notification"]',
                    '.alert-banner', '.promo-banner', '.sticky-banner',
                    
                    // Specific common IDs
                    '#onetrust-consent-sdk', '#CybotCookieDialog', '#cookie-law-info-bar',
                    '#cookie-bar', '.cookie-bar', '#cc-window', '.cc-window',
                    '#eu-cookie', '.eu-cookie', '#cookieDirective', '.cookieDirective'
                ];
                
                // Try to find and close banners
                for (const selector of selectors) {
                    try {
                        const elements = document.querySelectorAll(selector);
                        elements.forEach(element => {
                            // Check if element is visible
                            const style = window.getComputedStyle(element);
                            const isVisible = style.display !== 'none' && 
                                            style.visibility !== 'hidden' && 
                                            style.opacity !== '0' &&
                                            element.offsetWidth > 0 && 
                                            element.offsetHeight > 0;
                            
                            if (isVisible) {
                                // Try to find close button within the element
                                const closeButtons = element.querySelectorAll(
                                    'button[class*="close"], ' +
                                    'button[class*="Close"], ' +
                                    'button[aria-label*="close" i], ' +
                                    'button[aria-label*="dismiss" i], ' +
                                    'button[title*="close" i], ' +
                                    '.close, .Close, [class*="close-button"], ' +
                                    '[class*="dismiss"], [class*="accept"], ' +
                                    '[id*="close"], [id*="Close"], ' +
                                    '[class*="cookie-accept"], ' +
                                    '[class*="cookie-decline"], ' +
                                    '[class*="cookie-dismiss"]'
                                );
                                
                                if (closeButtons.length > 0) {
                                    // Click the first close button
                                    closeButtons[0].click();
                                    closed++;
                                } else {
                                    // No close button found, try to hide the element directly
                                    element.style.display = 'none';
                                    element.style.visibility = 'hidden';
                                    element.style.opacity = '0';
                                    element.style.height = '0';
                                    element.style.overflow = 'hidden';
                                    closed++;
                                }
                            }
                        });
                    } catch (e) {
                        // Continue with next selector
                    }
                }
                
                // Also try common close button selectors globally
                const globalCloseSelectors = [
                    'button[aria-label*="close" i]',
                    'button[aria-label*="dismiss" i]',
                    'button[title*="close" i]',
                    '.close-button', '.dismiss-button', '.accept-button',
                    '[data-dismiss="modal"]', '[data-bs-dismiss="modal"]'
                ];
                
                for (const selector of globalCloseSelectors) {
                    try {
                        const buttons = document.querySelectorAll(selector);
                        buttons.forEach(button => {
                            const style = window.getComputedStyle(button);
                            if (style.display !== 'none' && button.offsetWidth > 0) {
                                button.click();
                                closed++;
                            }
                        });
                    } catch (e) {
                        // Continue
                    }
                }
                
                return closed;
            }
        """)
        
        banners_closed = closed_count or 0
        
        # If we closed some banners, wait a bit for animations
        if banners_closed > 0:
            await asyncio.sleep(1)
            
            # Try one more time to catch any that appeared after first attempt
            additional_closed = await page.evaluate("""
                () => {
                    let closed = 0;
                    const selectors = [
                        '[id*="cookie"]', '[class*="cookie"]', '[id*="newsletter"]', 
                        '[class*="newsletter"]', '.modal', '.overlay', '.popup'
                    ];
                    
                    for (const selector of selectors) {
                        try {
                            const elements = document.querySelectorAll(selector);
                            elements.forEach(element => {
                                const style = window.getComputedStyle(element);
                                if (style.display !== 'none' && element.offsetHeight > 0) {
                                    element.style.display = 'none';
                                    closed++;
                                }
                            });
                        } catch (e) {}
                    }
                    return closed;
                }
            """)
            
            banners_closed += (additional_closed or 0)
        
    except Exception as e:
        ultra_safe_log_print(f"⚠️  Banner handling error: {str(e)[:50]}")
        # Continue anyway - don't fail the whole process
    
    return banners_closed

async def extract_wpforms_fields(page, form_load_timestamp: Optional[float] = None) -> Dict[str, Any]:
    """
    Extract all WPForms-specific fields from the form.
    Returns a dictionary with all fields needed for WPForms submission.
    """
    if not page or page.is_closed():
        return {}
    
    try:
        wpforms_data = await page.evaluate("""
            (formLoadTimestamp) => {
                const result = {
                    is_wpforms: false,
                    token: null,
                    token_time: null,
                    form_id: null,
                    post_id: null,
                    page_id: null,
                    page_url: null,
                    page_title: null,
                    url_referer: null,
                    start_timestamp: formLoadTimestamp ? Math.floor(formLoadTimestamp) : null,
                    end_timestamp: null,
                    submit: null,
                    hidden_fields: {}
                };
                
                // Check if this is a WPForms form
                const forms = document.querySelectorAll('form');
                let wpformsForm = null;
                
                for (const form of forms) {
                    // Check for WPForms indicators
                    if (form.id && form.id.includes('wpforms-form')) {
                        wpformsForm = form;
                        result.is_wpforms = true;
                        break;
                    }
                    if (form.className && form.className.includes('wpforms-form')) {
                        wpformsForm = form;
                        result.is_wpforms = true;
                        break;
                    }
                    if (form.dataset.formid || form.dataset.token) {
                        wpformsForm = form;
                        result.is_wpforms = true;
                        break;
                    }
                    // Check for wpforms fields
                    const hasWpformsFields = form.querySelector('input[name*="wpforms"]');
                    if (hasWpformsFields) {
                        wpformsForm = form;
                        result.is_wpforms = true;
                        break;
                    }
                }
                
                if (!wpformsForm) {
                    return result;
                }
                
                // Check if WPForms uses AJAX submission
                result.uses_ajax = wpformsForm.classList.contains('wpforms-ajax-form') || 
                                   wpformsForm.classList.contains('wpforms-form') ||
                                   wpformsForm.hasAttribute('data-token');
                
                // Get AJAX URL (usually /wp-admin/admin-ajax.php)
                if (result.uses_ajax) {
                    // Try to find AJAX URL from wpforms settings
                    if (window.wpforms && window.wpforms.settings) {
                        result.ajax_url = window.wpforms.settings.ajaxurl || '/wp-admin/admin-ajax.php';
                    } else {
                        // Default WPForms AJAX endpoint
                        result.ajax_url = '/wp-admin/admin-ajax.php';
                    }
                }
                
                // Extract data-token and data-token-time from form
                if (wpformsForm.dataset.token) {
                    result.token = wpformsForm.dataset.token;
                }
                if (wpformsForm.dataset.tokenTime) {
                    result.token_time = parseInt(wpformsForm.dataset.tokenTime) || null;
                }
                
                // Extract form ID from data-formid or form ID attribute
                if (wpformsForm.dataset.formid) {
                    result.form_id = wpformsForm.dataset.formid;
                } else if (wpformsForm.id) {
                    const formIdMatch = wpformsForm.id.match(/wpforms-form-(\d+)/);
                    if (formIdMatch) {
                        result.form_id = formIdMatch[1];
                    }
                }
                
                // Extract all hidden fields
                const hiddenInputs = wpformsForm.querySelectorAll('input[type="hidden"]');
                hiddenInputs.forEach(input => {
                    const name = input.name || input.id;
                    const value = input.value || '';
                    
                    if (name) {
                        result.hidden_fields[name] = value;
                        
                        // Extract specific WPForms fields
                        if (name.includes('wpforms[id]') || name === 'wpforms[id]') {
                            result.form_id = result.form_id || value;
                        } else if (name.includes('wpforms[post_id]') || name === 'wpforms[post_id]') {
                            result.post_id = value;
                        } else if (name === 'page_id') {
                            result.page_id = value;
                        } else if (name === 'page_url') {
                            result.page_url = value;
                        } else if (name === 'page_title') {
                            result.page_title = value;
                        } else if (name === 'url_referer') {
                            result.url_referer = value;
                        } else if (name.includes('wpforms[token]') || name === 'wpforms[token]') {
                            result.token = result.token || value;
                        }
                    }
                });
                
                // If token not found in hidden fields, try to get from data-token
                if (!result.token && wpformsForm.dataset.token) {
                    result.token = wpformsForm.dataset.token;
                }
                
                // Get page info if not in hidden fields
                if (!result.page_url) {
                    result.page_url = window.location.href;
                }
                if (!result.page_title) {
                    result.page_title = document.title || '';
                }
                
                // Generate end_timestamp (current time in seconds)
                result.end_timestamp = Math.floor(Date.now() / 1000);
                
                // If start_timestamp not provided, use a reasonable default (5 seconds before end)
                if (!result.start_timestamp) {
                    result.start_timestamp = result.end_timestamp - 5;
                }
                
                // Set submit field (WPForms uses 'wpforms-submit' for AJAX, not form ID)
                result.submit = 'wpforms-submit';
                
                return result;
            }
        """, form_load_timestamp)
        
        return wpforms_data
    except Exception as e:
        ultra_safe_log_print(f"   ⚠️  Error extracting WPForms fields: {str(e)[:100]}")
        return {}


async def inject_wpforms_fields(page, wpforms_data: Dict[str, Any]) -> bool:
    """
    Inject all WPForms fields into the form before submission.
    This ensures the POST payload has all required fields.
    """
    if not page or page.is_closed() or not wpforms_data.get('is_wpforms'):
        return False
    
    try:
        success = await page.evaluate("""
            (wpformsData) => {
                try {
                    const forms = document.querySelectorAll('form');
                    let wpformsForm = null;
                    
                    // Find WPForms form
                    for (const form of forms) {
                        if (form.id && form.id.includes('wpforms-form')) {
                            wpformsForm = form;
                            break;
                        }
                        if (form.className && form.className.includes('wpforms-form')) {
                            wpformsForm = form;
                            break;
                        }
                        if (form.dataset.formid || form.dataset.token) {
                            wpformsForm = form;
                            break;
                        }
                        const hasWpformsFields = form.querySelector('input[name*="wpforms"]');
                        if (hasWpformsFields) {
                            wpformsForm = form;
                            break;
                        }
                    }
                    
                    if (!wpformsForm) {
                        return false;
                    }
                    
                    // Inject wpforms[token] from data-token
                    if (wpformsData.token) {
                        let tokenInput = wpformsForm.querySelector('input[name="wpforms[token]"]');
                        if (!tokenInput) {
                            // Create the input if it doesn't exist
                            tokenInput = document.createElement('input');
                            tokenInput.type = 'hidden';
                            tokenInput.name = 'wpforms[token]';
                            wpformsForm.appendChild(tokenInput);
                        }
                        tokenInput.value = wpformsData.token;
                    }
                    
                    // Inject start_timestamp
                    if (wpformsData.start_timestamp) {
                        let startInput = wpformsForm.querySelector('input[name="start_timestamp"]');
                        if (!startInput) {
                            startInput = document.createElement('input');
                            startInput.type = 'hidden';
                            startInput.name = 'start_timestamp';
                            wpformsForm.appendChild(startInput);
                        }
                        startInput.value = wpformsData.start_timestamp.toString();
                    }
                    
                    // Inject end_timestamp
                    if (wpformsData.end_timestamp) {
                        let endInput = wpformsForm.querySelector('input[name="end_timestamp"]');
                        if (!endInput) {
                            endInput = document.createElement('input');
                            endInput.type = 'hidden';
                            endInput.name = 'end_timestamp';
                            wpformsForm.appendChild(endInput);
                        }
                        endInput.value = wpformsData.end_timestamp.toString();
                    }
                    
                    // Inject wpforms[id] if we have form_id
                    if (wpformsData.form_id) {
                        let formIdInput = wpformsForm.querySelector('input[name="wpforms[id]"]');
                        if (!formIdInput) {
                            formIdInput = document.createElement('input');
                            formIdInput.type = 'hidden';
                            formIdInput.name = 'wpforms[id]';
                            wpformsForm.appendChild(formIdInput);
                        }
                        formIdInput.value = wpformsData.form_id;
                    }
                    
                    // Inject wpforms[submit]
                    if (wpformsData.submit) {
                        let submitInput = wpformsForm.querySelector('input[name="wpforms[submit]"]');
                        if (!submitInput) {
                            submitInput = document.createElement('input');
                            submitInput.type = 'hidden';
                            submitInput.name = 'wpforms[submit]';
                            wpformsForm.appendChild(submitInput);
                        }
                        submitInput.value = wpformsData.submit;
                    }
                    
                    // Inject action field for AJAX submission
                    if (wpformsData.uses_ajax) {
                        let actionInput = wpformsForm.querySelector('input[name="action"]');
                        if (!actionInput) {
                            actionInput = document.createElement('input');
                            actionInput.type = 'hidden';
                            actionInput.name = 'action';
                            wpformsForm.appendChild(actionInput);
                        }
                        actionInput.value = 'wpforms_submit';
                    }
                    
                    // Inject other hidden fields if they don't exist
                    for (const [name, value] of Object.entries(wpformsData.hidden_fields || {})) {
                        if (name && value) {
                            let existingInput = wpformsForm.querySelector(`input[name="${name}"]`);
                            if (!existingInput) {
                                existingInput = document.createElement('input');
                                existingInput.type = 'hidden';
                                existingInput.name = name;
                                wpformsForm.appendChild(existingInput);
                            }
                            existingInput.value = value;
                        }
                    }
                    
                    // Update form data attributes if needed
                    if (wpformsData.token && !wpformsForm.dataset.token) {
                        wpformsForm.setAttribute('data-token', wpformsData.token);
                    }
                    if (wpformsData.token_time && !wpformsForm.dataset.tokenTime) {
                        wpformsForm.setAttribute('data-token-time', wpformsData.token_time.toString());
                    }
                    
                    return true;
                } catch (e) {
                    console.error('Error injecting WPForms fields:', e);
                    return false;
                }
            }
        """, wpforms_data)
        
        return success
    except Exception as e:
        ultra_safe_log_print(f"   ⚠️  Error injecting WPForms fields: {str(e)[:100]}")
        return False


async def ultra_simple_form_fill(page, template: Dict[str, Any]) -> Dict[str, Any]:
    """ULTRA-RESILIENT simple form filling that cannot fail."""
    result = {
        "fields_attempted": 0,
        "fields_filled": 0,
        "checkboxes_checked": 0
    }
    
    if not page or page.is_closed():
        return result
    
    try:
        # First, identify the contact form (not newsletter form)
        # Contact form typically has: name, email, phone, comment/message fields
        # Newsletter form typically only has: email field
        contact_form_info = await page.evaluate("""
            () => {
                const forms = Array.from(document.querySelectorAll('form'));
                let contactForm = null;
                let maxContactFields = 0;
                
                forms.forEach(form => {
                    const fields = form.querySelectorAll('input, textarea');
                    let hasName = false;
                    let hasEmail = false;
                    let hasPhone = false;
                    let hasComment = false;
                    const fieldNames = [];
                    
                    fields.forEach(field => {
                        if (field.type === 'submit' || field.type === 'button' || field.type === 'hidden') {
                            return;
                        }
                        const name = (field.name || field.id || '').toLowerCase();
                        fieldNames.push(name);
                        
                        // Check for specific contact form field names
                        if (name === 'name' || name.includes('naam')) hasName = true;
                        if (name === 'email') hasEmail = true;
                        if (name === 'phone' || name === 'telefoon') hasPhone = true;
                        if (name === 'comment' || name === 'message' || name === 'bericht') hasComment = true;
                    });
                    
                    // Contact form must have: name, email, and comment/message (at least 3 of these)
                    const contactFieldCount = (hasName ? 1 : 0) + (hasEmail ? 1 : 0) + (hasPhone ? 1 : 0) + (hasComment ? 1 : 0);
                    
                    // Prioritize forms with name + email + comment (typical contact form)
                    if (hasName && hasEmail && hasComment && contactFieldCount > maxContactFields) {
                        maxContactFields = contactFieldCount;
                        contactForm = form;
                    } else if (contactFieldCount >= 3 && contactFieldCount > maxContactFields) {
                        maxContactFields = contactFieldCount;
                        contactForm = form;
                    }
                });
                
                // If contact form found, focus on it by scrolling to it
                if (contactForm) {
                    contactForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    // Also try to find the contactInfo section
                    const contactSection = contactForm.closest('.contactInfo, section');
                    if (contactSection) {
                        contactSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                    return { found: true, fieldCount: maxContactFields };
                }
                
                return { found: false, fieldCount: 0 };
            }
        """)
        
        if contact_form_info.get('found'):
            ultra_safe_log_print(f"   ✅ Contact form identified (has {contact_form_info.get('fieldCount')} contact fields: name, email, phone, comment)")
        else:
            ultra_safe_log_print("   ⚠️  Contact form not clearly identified, will fill all forms")
        
        await asyncio.sleep(1)  # Wait for scroll
        
        # Comprehensive field detection and filling
        fill_result = await page.evaluate("""
            () => {
                try {
                    let filled = 0;
                    let selects_filled = 0;
                    
                    // Fill text inputs, email, phone, textarea
                    // Prioritize contact form fields (name, email, phone, comment)
                    const text_inputs = document.querySelectorAll('input[type="text"], input[type="email"], input[type="tel"], input[type="number"], textarea');
                    text_inputs.forEach(input => {
                        try {
                            if (!input.value && input.offsetParent !== null && !input.disabled) {
                                const name = (input.name || '').toLowerCase();
                                const placeholder = (input.placeholder || '').toLowerCase();
                                
                                // Skip newsletter forms (only email field, no name/comment)
                                const form = input.closest('form');
                                if (form) {
                                    const formFields = Array.from(form.querySelectorAll('input, textarea'));
                                    const hasName = formFields.some(f => (f.name || '').toLowerCase() === 'name');
                                    const hasComment = formFields.some(f => (f.name || '').toLowerCase() === 'comment' || (f.name || '').toLowerCase() === 'message');
                                    // If form only has email and no name/comment, it's likely newsletter - skip it if we found a contact form
                                    if (!hasName && !hasComment && name === 'email' && formFields.length <= 2) {
                                        return; // Skip newsletter form
                                    }
                                }
                                
                                // If field has no name, try to add one based on type/placeholder
                                if (!input.name && !input.id) {
                                    if (input.type === 'email' || placeholder.includes('email')) {
                                        input.name = 'email';
                                    } else if (placeholder.includes('name')) {
                                        input.name = 'name';
                                    } else if (placeholder.includes('phone') || input.type === 'tel') {
                                        input.name = 'phone';
                                    } else if (placeholder.includes('message') || input.tagName === 'TEXTAREA') {
                                        input.name = 'message';
                                    } else {
                                        input.name = 'field_' + filled; // Generic name
                                    }
                                }
                                
                                // Determine value to fill
                                const currentName = (input.name || input.id || '').toLowerCase();
                                let valueToFill = 'Test Value';
                                if (input.type === 'email' || currentName.includes('email') || placeholder.includes('email') || placeholder.includes('e-mailadres')) {
                                    valueToFill = 'test@example.com';
                                } else if (currentName.includes('name') || placeholder.includes('naam') || placeholder.includes('name')) {
                                    valueToFill = 'Test User';
                                } else if (currentName.includes('phone') || currentName.includes('telefoon') || placeholder.includes('phone') || placeholder.includes('nummer') || input.type === 'tel') {
                                    valueToFill = '+1234567890';
                                } else if (currentName.includes('message') || currentName.includes('comment') || currentName.includes('bericht') || placeholder.includes('message') || placeholder.includes('bericht') || input.tagName === 'TEXTAREA') {
                                    valueToFill = 'This is an automated test submission.';
                                }
                                
                                // For React/Next.js controlled components, use native setter
                                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
                                const nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")?.set;
                                
                                if (input.tagName === 'INPUT' && nativeInputValueSetter) {
                                    nativeInputValueSetter.call(input, valueToFill);
                                } else if (input.tagName === 'TEXTAREA' && nativeTextAreaValueSetter) {
                                    nativeTextAreaValueSetter.call(input, valueToFill);
                                } else {
                                    input.value = valueToFill;
                                }
                                
                                // Trigger React's synthetic events with proper target
                                const inputEvent = new Event('input', { bubbles: true, cancelable: true });
                                const changeEvent = new Event('change', { bubbles: true, cancelable: true });
                                Object.defineProperty(inputEvent, 'target', { value: input, enumerable: true });
                                Object.defineProperty(changeEvent, 'target', { value: input, enumerable: true });
                                
                                input.dispatchEvent(inputEvent);
                                input.dispatchEvent(changeEvent);
                                
                                // Also trigger focus/blur to ensure React state updates
                                input.focus();
                                input.dispatchEvent(new Event('focus', { bubbles: true }));
                                input.dispatchEvent(new Event('blur', { bubbles: true }));
                                
                                // Update React's internal value tracker if available
                                if (input._valueTracker) {
                                    input._valueTracker.setValue('');
                                    input._valueTracker.setValue(valueToFill);
                                }
                                
                                filled++;
                            }
                        } catch (e) {}
                    });
                    
                    // Fill select dropdowns
                    const selects = document.querySelectorAll('select');
                    selects.forEach(select => {
                        try {
                            if (select.offsetParent !== null && !select.disabled) {
                                const options = Array.from(select.options).filter(opt => 
                                    opt.value && opt.value.trim() && !opt.disabled &&
                                    !opt.value.toLowerCase().includes('select') &&
                                    !opt.value.toLowerCase().includes('choose')
                                );
                                
                                if (options.length > 0) {
                                    // Select a random option
                                    const randomOption = options[Math.floor(Math.random() * options.length)];
                                    select.value = randomOption.value;
                                    select.dispatchEvent(new Event('change', { bubbles: true }));
                                    selects_filled++;
                                }
                            }
                        } catch (e) {}
                    });
                    
                    return { filled, selects_filled };
                } catch (e) {
                    return { filled: 0, selects_filled: 0 };
                }
            }
        """)
        
        result["fields_filled"] = fill_result.get("filled", 0) + fill_result.get("selects_filled", 0)
        
        # For React/Next.js forms, also try Playwright's fill() method which handles controlled components better
        # Prioritize contact form fields (name, email, phone, comment)
        try:
            # First, try to find the contact form in the contactInfo section
            contact_form_section = await page.query_selector('.contactInfo form, section.contactInfo form')
            if contact_form_section:
                ultra_safe_log_print("   ✅ Found contact form in contactInfo section")
                # Scroll to the contact form section
                await contact_form_section.scroll_into_view_if_needed()
                await asyncio.sleep(0.5)
            
            # Try to find contact form fields specifically (name, email, phone, comment)
            contact_form_fields = await page.query_selector_all('input[name="name"], input[name="email"], input[name="phone"], textarea[name="comment"]')
            
            if len(contact_form_fields) >= 3:  # Found contact form (has at least name, email, comment)
                ultra_safe_log_print("   ✅ Found contact form fields (name, email, phone, comment)")
                for input_field in contact_form_fields:
                    try:
                        is_visible = await input_field.is_visible()
                        if not is_visible:
                            continue
                        
                        current_value = await input_field.input_value()
                        if not current_value or current_value.strip() == '':
                            name = await input_field.evaluate("(el) => (el.name || '').toLowerCase()")
                            
                            if name == 'name':
                                await input_field.fill('Test User')
                                ultra_safe_log_print("   ✅ Filled name field")
                            elif name == 'email':
                                await input_field.fill('test@example.com')
                                ultra_safe_log_print("   ✅ Filled email field")
                            elif name == 'phone':
                                await input_field.fill('+1234567890')
                                ultra_safe_log_print("   ✅ Filled phone field")
                            elif name == 'comment':
                                await input_field.fill('This is an automated test submission.')
                                ultra_safe_log_print("   ✅ Filled comment field")
                            
                            await asyncio.sleep(0.2)
                    except:
                        continue
            
            # Also fill other fields as fallback
            all_inputs = await page.query_selector_all('input[type="text"], input[type="email"], input[type="tel"], textarea')
            for input_field in all_inputs:
                try:
                    is_visible = await input_field.is_visible()
                    if not is_visible:
                        continue
                    
                    current_value = await input_field.input_value()
                    if not current_value or current_value.strip() == '':
                        # Determine what to fill
                        name = await input_field.evaluate("(el) => (el.name || el.id || '').toLowerCase()")
                        placeholder = await input_field.evaluate("(el) => (el.placeholder || '').toLowerCase()")
                        input_type = await input_field.evaluate("(el) => el.type || ''")
                        tag_name = await input_field.evaluate("(el) => el.tagName.toLowerCase()")
                        
                        value_to_fill = 'test@example.com'
                        if input_type == 'email' or 'email' in name or 'email' in placeholder or 'e-mailadres' in placeholder:
                            value_to_fill = 'test@example.com'
                        elif 'name' in name or 'naam' in placeholder or 'name' in placeholder:
                            value_to_fill = 'Test User'
                        elif 'phone' in name or 'telefoon' in name or 'phone' in placeholder or 'nummer' in placeholder or input_type == 'tel':
                            value_to_fill = '+1234567890'
                        elif 'message' in name or 'comment' in name or 'bericht' in name or 'message' in placeholder or 'bericht' in placeholder or tag_name == 'textarea':
                            value_to_fill = 'This is an automated test submission.'
                        else:
                            value_to_fill = 'Test Value'
                        
                        # Use Playwright's fill() which properly handles React controlled components
                        await input_field.fill(value_to_fill)
                        await asyncio.sleep(0.2)
                        ultra_safe_log_print(f"   ✅ Filled field using Playwright fill(): {name or 'unnamed'}")
                except:
                    continue
        except:
            pass
        
        # Log all form fields and their values before submission
        try:
            form_fields_info = await page.evaluate("""
                () => {
                    const form = document.querySelector('form');
                    if (!form) return { found: false };
                    
                    const fields = [];
                    const allInputs = form.querySelectorAll('input, select, textarea');
                    
                    allInputs.forEach(field => {
                        if (field.type === 'submit' || field.type === 'button' || field.type === 'hidden') {
                            return; // Skip submit buttons and hidden fields (we'll log hidden separately)
                        }
                        
                        fields.push({
                            type: field.tagName.toLowerCase(),
                            name: field.name || field.id || 'unnamed',
                            value: field.value || '',
                            required: field.required,
                            placeholder: field.placeholder || '',
                            checked: field.checked || false
                        });
                    });
                    
                    // Also get hidden fields
                    const hiddenFields = form.querySelectorAll('input[type="hidden"]');
                    const hidden = [];
                    hiddenFields.forEach(field => {
                        hidden.push({
                            name: field.name || field.id || 'unnamed',
                            value: field.value || ''
                        });
                    });
                    
                    // Check for JavaScript submission handlers
                    const submitButton = form.querySelector('button[type="submit"], input[type="submit"]');
                    const hasOnSubmit = form.onsubmit !== null;
                    const hasSubmitListener = submitButton && (submitButton.onclick !== null || submitButton.addEventListener);
                    
                    // Check if form uses AJAX/JavaScript submission
                    const formHTML = form.outerHTML.toLowerCase();
                    const usesAJAX = formHTML.includes('fetch') || formHTML.includes('xmlhttprequest') || 
                                   formHTML.includes('axios') || formHTML.includes('.submit(') ||
                                   formHTML.includes('preventdefault') || formHTML.includes('onsubmit');
                    
                    return {
                        found: true,
                        fields: fields,
                        hidden: hidden,
                        action: form.action || window.location.href,
                        method: form.method || 'get',
                        hasOnSubmit: hasOnSubmit,
                        hasSubmitListener: hasSubmitListener,
                        usesAJAX: usesAJAX,
                        formHTML: form.outerHTML.substring(0, 500) // First 500 chars for inspection
                    };
                }
            """)
            
            if form_fields_info.get('found'):
                ultra_safe_log_print(f"   📋 Form fields before submission:")
                for field in form_fields_info.get('fields', []):
                    value_preview = field['value'][:50] if field['value'] else '(empty)'
                    required_mark = " [REQUIRED]" if field['required'] else ""
                    ultra_safe_log_print(f"      - {field['name']}: {value_preview}{required_mark}")
                
                hidden_fields = form_fields_info.get('hidden', [])
                if hidden_fields:
                    ultra_safe_log_print(f"   🔒 Hidden fields ({len(hidden_fields)}):")
                    for field in hidden_fields:
                        value_preview = field['value'][:50] if field['value'] else '(empty)'
                        ultra_safe_log_print(f"      - {field['name']}: {value_preview}")
                
                # Check for JavaScript submission
                if form_fields_info.get('usesAJAX') or form_fields_info.get('hasOnSubmit'):
                    ultra_safe_log_print(f"   ⚠️  Form may use JavaScript/AJAX submission!")
                    ultra_safe_log_print(f"      - hasOnSubmit: {form_fields_info.get('hasOnSubmit')}")
                    ultra_safe_log_print(f"      - usesAJAX: {form_fields_info.get('usesAJAX')}")
                    ultra_safe_log_print(f"   💡 Will try button click to trigger JavaScript submission")
                
                # Log form HTML structure for debugging
                form_html = form_fields_info.get('formHTML', '')
                if form_html:
                    ultra_safe_log_print(f"   🔍 Form HTML preview (first 300 chars): {form_html[:300]}")
                    
                    # Check for common form field patterns that might be missing
                    if 'name' not in form_html.lower() and len(form_fields_info.get('fields', [])) == 1:
                        ultra_safe_log_print(f"   ⚠️  Form only has 1 field - might need additional fields (name, message, etc.)")
                    if 'message' not in form_html.lower() and 'textarea' not in form_html.lower():
                        ultra_safe_log_print(f"   ⚠️  No message/textarea field found - form might be incomplete")
        except Exception as e:
            ultra_safe_log_print(f"   ⚠️  Could not log form fields: {str(e)[:50]}")
        
        # Comprehensive checkbox checking (including groups) - use Playwright for reliability
        try:
            all_checkboxes = await page.query_selector_all('input[type="checkbox"]')
            checked_count = 0
            checkbox_groups = {}
            
            ultra_safe_log_print(f"   🔍 Found {len(all_checkboxes)} checkbox(es) on page")
            
            # Group checkboxes by name
            for checkbox in all_checkboxes:
                try:
                    is_visible = await checkbox.is_visible()
                    is_disabled = await checkbox.is_disabled()
                    if not is_visible or is_disabled:
                        continue
                    
                    name = await checkbox.evaluate("(cb) => cb.name || cb.id || 'ungrouped'")
                    label = await checkbox.evaluate("(cb) => cb.closest('label')?.textContent || cb.getAttribute('aria-label') || ''")
                    value = await checkbox.evaluate("(cb) => cb.value || ''")
                    text = (name + ' ' + label + ' ' + value).lower()
                    
                    # Skip newsletter/marketing checkboxes (but only if text contains skip keywords)
                    # Don't skip if label is empty and it's part of a form field group (like interest[], services[], etc.)
                    skip_keywords = ['newsletter', 'marketing', 'subscribe', 'cookie', 'honeypot', 'remember']
                    should_skip = False
                    if text.strip() and any(kw in text for kw in skip_keywords):
                        should_skip = True
                    # Don't skip checkboxes in form field groups (array names like interest[], services[])
                    if '[]' in name or name.endswith('[]'):
                        should_skip = False  # These are form field groups, not marketing checkboxes
                    
                    if should_skip:
                        ultra_safe_log_print(f"   ⏭️  Skipping checkbox: {name[:30]} (newsletter/marketing)")
                        continue
                    
                    if name not in checkbox_groups:
                        checkbox_groups[name] = []
                    checkbox_groups[name].append(checkbox)
                    ultra_safe_log_print(f"   📋 Found checkbox: {name[:30]} (label: {label[:30]})")
                except Exception as e:
                    ultra_safe_log_print(f"   ⚠️  Error processing checkbox: {str(e)[:50]}")
                    continue
            
            # Check at least one in each group
            for group_name, group_checkboxes in checkbox_groups.items():
                try:
                    ultra_safe_log_print(f"   🔍 Processing checkbox group '{group_name}' ({len(group_checkboxes)} checkbox(es))")
                    # Check if any in group is already checked
                    any_checked = False
                    for cb in group_checkboxes:
                        if await cb.is_checked():
                            any_checked = True
                            checked_count += 1
                            ultra_safe_log_print(f"   ✅ Checkbox in group '{group_name}' already checked")
                            break
                    
                    # If none checked, check at least one (prefer first visible one)
                    if not any_checked and len(group_checkboxes) > 0:
                        import random
                        cb_to_check = random.choice(group_checkboxes)
                        try:
                            # Use JavaScript to check directly (more reliable)
                            checked_js = await cb_to_check.evaluate("""
                                (cb) => {
                                    try {
                                        if (!cb.checked) {
                                            cb.checked = true;
                                            cb.dispatchEvent(new Event('change', { bubbles: true }));
                                            cb.dispatchEvent(new Event('click', { bubbles: true }));
                                        }
                                        return cb.checked;
                                    } catch (e) {
                                        return false;
                                    }
                                }
                            """)
                            await asyncio.sleep(0.2)
                            if checked_js:
                                checked_count += 1
                                ultra_safe_log_print(f"   ✅ Checked checkbox in group '{group_name}' (via JavaScript)")
                            else:
                                # Fallback: try Playwright check with shorter timeout
                                try:
                                    await cb_to_check.check(timeout=2000)
                                    await asyncio.sleep(0.2)
                                    if await cb_to_check.is_checked():
                                        checked_count += 1
                                        ultra_safe_log_print(f"   ✅ Checked checkbox in group '{group_name}' (via Playwright)")
                                except:
                                    # Last resort: click
                                    try:
                                        await cb_to_check.click(timeout=2000)
                                        await asyncio.sleep(0.2)
                                        if await cb_to_check.is_checked():
                                            checked_count += 1
                                            ultra_safe_log_print(f"   ✅ Checked checkbox in group '{group_name}' (via click)")
                                    except:
                                        ultra_safe_log_print(f"   ⚠️  Could not check checkbox in group '{group_name}'")
                        except Exception as e:
                            ultra_safe_log_print(f"   ⚠️  Error checking checkbox in group '{group_name}': {str(e)[:50]}")
                except Exception as e:
                    ultra_safe_log_print(f"   ⚠️  Error processing checkbox group '{group_name}': {str(e)[:50]}")
                    continue
            
            checkbox_result = checked_count
        except:
            # Fallback to JavaScript
            checkbox_result = await page.evaluate("""
                () => {
                    try {
                        let checked = 0;
                        const checkboxGroups = {};
                        const checkboxes = document.querySelectorAll('input[type="checkbox"]');
                        const skipKeywords = ['newsletter', 'marketing', 'subscribe', 'cookie', 'honeypot'];
                        
                        // Group checkboxes by name
                        checkboxes.forEach(cb => {
                            if (cb.offsetParent !== null && !cb.disabled) {
                                const name = (cb.name || 'ungrouped').toLowerCase();
                                const label = (cb.closest('label')?.textContent || '').toLowerCase();
                                const text = name + ' ' + label;
                                
                                if (skipKeywords.some(kw => text.includes(kw))) {
                                    return;
                                }
                                
                                if (!checkboxGroups[name]) {
                                    checkboxGroups[name] = [];
                                }
                                checkboxGroups[name].push(cb);
                            }
                        });
                        
                        // Check at least one in each group
                        Object.keys(checkboxGroups).forEach(groupName => {
                            const group = checkboxGroups[groupName];
                            const anyChecked = group.some(cb => cb.checked);
                            
                            if (!anyChecked && group.length > 0) {
                                const randomCb = group[Math.floor(Math.random() * group.length)];
                                randomCb.checked = true;
                                randomCb.click();
                                randomCb.dispatchEvent(new Event('change', { bubbles: true }));
                                checked++;
                            } else {
                                group.forEach(cb => {
                                    if (cb.checked) checked++;
                                });
                            }
                        });
                        
                        return checked;
                    } catch (e) {
                        return 0;
                    }
                }
            """)
        
        result["checkboxes_checked"] = checkbox_result
        result["fields_attempted"] = result["fields_filled"] + result["checkboxes_checked"]
        
        ultra_safe_log_print(f"   ✅ Filled {result['fields_filled']} field(s), checked {result['checkboxes_checked']} checkbox(es)")
        
        # Verify all required fields are filled and fill any missing ones
        try:
            required_check = await page.evaluate("""
                () => {
                    const form = document.querySelector('form');
                    if (!form) return { empty_required: [] };
                    
                    const empty_required = [];
                    const allFields = form.querySelectorAll('input, select, textarea');
                    
                    allFields.forEach(field => {
                        if (field.type === 'submit' || field.type === 'button' || field.type === 'hidden') {
                            return;
                        }
                        
                        if (field.required) {
                            const isEmpty = !field.value || field.value.trim() === '' || 
                                          (field.type === 'checkbox' && !field.checked) ||
                                          (field.tagName === 'SELECT' && (!field.value || field.value === '' || field.value === '0'));
                            
                            if (isEmpty) {
                                empty_required.push({
                                    name: field.name || field.id || 'unnamed',
                                    type: field.type || field.tagName.toLowerCase(),
                                    placeholder: field.placeholder || ''
                                });
                            }
                        }
                    });
                    
                    return { empty_required };
                }
            """)
            
            empty_required = required_check.get('empty_required', [])
            if empty_required:
                ultra_safe_log_print(f"   ⚠️  Found {len(empty_required)} empty required field(s), attempting to fill...")
                
                # Try to fill empty required fields
                for field_info in empty_required:
                    try:
                        field_name = field_info['name'].lower()
                        field_type = field_info['type'].lower()
                        placeholder = field_info.get('placeholder', '').lower()
                        
                        # Determine what value to use
                        if 'email' in field_name or 'email' in placeholder or field_type == 'email':
                            value = 'test@example.com'
                        elif 'name' in field_name or 'name' in placeholder:
                            value = 'Test User'
                        elif 'phone' in field_name or 'phone' in placeholder or field_type == 'tel':
                            value = '+1234567890'
                        elif 'message' in field_name or 'message' in placeholder:
                            value = 'This is an automated test submission.'
                        else:
                            value = 'Test Value'
                        
                        # Fill the field
                        filled = await page.evaluate(f"""
                            (fieldName, value) => {{
                                const form = document.querySelector('form');
                                if (!form) return false;
                                
                                const field = form.querySelector(`[name="${{fieldName}}"], #${{fieldName}}`);
                                if (!field) return false;
                                
                                if (field.type === 'checkbox' || field.type === 'radio') {{
                                    field.checked = true;
                                    field.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                }} else {{
                                    field.value = value;
                                    field.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    field.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                }}
                                
                                return true;
                            }}
                        """, field_info['name'], value)
                        
                        if filled:
                            ultra_safe_log_print(f"   ✅ Filled required field: {field_info['name']}")
                            result["fields_filled"] += 1
                    except Exception as e:
                        ultra_safe_log_print(f"   ⚠️  Could not fill required field {field_info['name']}: {str(e)[:50]}")
            else:
                ultra_safe_log_print(f"   ✅ All required fields are filled")
        except Exception as e:
            ultra_safe_log_print(f"   ⚠️  Required fields check failed: {str(e)[:50]}")
        
    except Exception:
        pass  # Silent failure - we tried
    
    return result

async def ultra_simple_form_submit(page) -> Dict[str, Any]:
    """ULTRA-RESILIENT form submission with proper POST tracking."""
    result = {
        "submission_attempted": False,
        "submission_success": False,
        "method_used": "none",
        "post_requests": 0,
        "post_responses": 0,
        "form_submission_detected": False
    }
    
    if not page or page.is_closed():
        return result
    
    # Find all forms and identify the contact form (skip search forms)
    contact_form_found = False
    target_form = None
    try:
        forms_info = await page.evaluate("""
            () => {
                const allForms = Array.from(document.querySelectorAll('form'));
                if (allForms.length === 0) return { found: false, forms: [] };
                
                const formsData = [];
                
                for (const form of allForms) {
                    const method = (form.method || 'get').toLowerCase();
                    const action = form.action || '';
                    const formText = form.textContent.toLowerCase();
                    const formId = (form.id || '').toLowerCase();
                    const formClass = (form.className || '').toLowerCase();
                    const role = form.getAttribute('role') || '';
                    
                    // Check if it's a search form
                    const isSearch = (
                        role === 'search' ||
                        (method === 'get' && (
                            formText.includes('search') ||
                            formId.includes('search') ||
                            formClass.includes('search') ||
                            action.includes('search') ||
                            form.querySelector('input[type="search"]') ||
                            form.querySelector('input[name*="search"]') ||
                            form.querySelector('input[name*="q"]') ||
                            form.querySelector('input[name="s"]')
                        ))
                    );
                    
                    // Check if it's a contact form
                    const isContact = (
                        formText.includes('contact') ||
                        formId.includes('contact') ||
                        formClass.includes('contact') ||
                        action.includes('contact') ||
                        form.querySelector('input[name*="email"]') ||
                        form.querySelector('input[name*="name"]') ||
                        form.querySelector('textarea[name*="message"]') ||
                        form.querySelector('textarea[name*="comment"]') ||
                        form.querySelector('input[type="email"]') ||
                        (method === 'post' && !isSearch)
                    );
                    
                    formsData.push({
                        method: method,
                        action: form.action ? new URL(form.action, window.location.href).href : window.location.href,
                        isSearch: isSearch,
                        isContact: isContact,
                        hasEmail: !!form.querySelector('input[type="email"], input[name*="email"]'),
                        hasName: !!form.querySelector('input[name*="name"]'),
                        hasMessage: !!form.querySelector('textarea'),
                        isPost: method === 'post',
                        formIndex: formsData.length
                    });
                }
                
                return {
                    found: true,
                    forms: formsData,
                    totalForms: allForms.length
                };
            }
        """)
        
        if forms_info.get('found'):
            total_forms = forms_info.get('totalForms', 0)
            ultra_safe_log_print(f"   🔍 Found {total_forms} form(s) on page")
            
            forms_data = forms_info.get('forms', [])
            
            # First, try to find a contact form
            contact_form_index = None
            for i, form_data in enumerate(forms_data):
                if form_data.get('isContact'):
                    contact_form_index = i
                    contact_form_found = True
                    ultra_safe_log_print(f"   ✅ Contact form detected (form #{i+1})")
                    break
            
            # If no contact form found, look for any POST form that's not a search form
            if contact_form_index is None:
                for i, form_data in enumerate(forms_data):
                    if form_data.get('isPost') and not form_data.get('isSearch'):
                        contact_form_index = i
                        ultra_safe_log_print(f"   ✅ Found POST form (form #{i+1}) - likely contact form")
                        break
            
            # If still no form found, look for any form with email field
            if contact_form_index is None:
                for i, form_data in enumerate(forms_data):
                    if form_data.get('hasEmail') and not form_data.get('isSearch'):
                        contact_form_index = i
                        ultra_safe_log_print(f"   ✅ Found form with email field (form #{i+1}) - likely contact form")
                        break
            
            # Skip search forms
            search_forms_count = sum(1 for f in forms_data if f.get('isSearch'))
            if search_forms_count > 0:
                ultra_safe_log_print(f"   ⏭️  Skipping {search_forms_count} search form(s)")
            
            if contact_form_index is not None:
                target_form_data = forms_data[contact_form_index]
                form_action_url = target_form_data.get('action', page.url)
                form_method = target_form_data.get('method', 'get')
                ultra_safe_log_print(f"   📋 Form action URL: {form_action_url[:80]}")
                ultra_safe_log_print(f"   📋 Form method: {form_method.upper()}")
                
                # Store form index for later use
                target_form = contact_form_index
            else:
                ultra_safe_log_print("   ⚠️  No suitable contact form found")
                # Try to find contact page link
                contact_link = await page.evaluate("""
                    () => {
                        const links = Array.from(document.querySelectorAll('a[href*="contact"]'));
                        if (links.length > 0) {
                            return links[0].href;
                        }
                        return null;
                    }
                """)
                if contact_link:
                    ultra_safe_log_print(f"   🔗 Found contact link: {contact_link[:80]}")
                    ultra_safe_log_print("   ⚠️  Please navigate to contact page manually or update URL")
                form_action_url = page.url
        else:
            # No form found, try to find contact page link
            ultra_safe_log_print("   ⚠️  No form found on page, looking for contact page...")
            contact_link = await page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href*="contact"]'));
                    if (links.length > 0) {
                        return links[0].href;
                    }
                    return null;
                }
            """)
            if contact_link:
                ultra_safe_log_print(f"   🔗 Found contact link: {contact_link[:80]}")
                ultra_safe_log_print("   ⚠️  Please navigate to contact page manually or update URL")
            form_action_url = page.url
    except:
        try:
            form_action_url = page.url
        except:
            form_action_url = ""
    
    # Store target form index in window for JavaScript access
    if target_form is not None:
        await page.evaluate(f"window.__targetFormIndex = {target_form};")
    else:
        await page.evaluate("window.__targetFormIndex = null;")
    
    # If no target form found, return early
    if target_form is None and not contact_form_found:
        ultra_safe_log_print("   ⚠️  No contact form found to submit")
        result["submission_attempted"] = False
        result["submission_success"] = False
        result["error"] = "No contact form found"
        return result
    
    # Track POST and GET requests and responses (GET for contact forms)
    post_requests = []
    post_responses = []
    get_requests = []
    get_responses = []
    form_submission_detected = False
    form_submission_data = None
    form_method = "POST"  # Default, will be updated
    
    def track_request(request):
        nonlocal form_submission_data, form_submission_detected
        if request.method == "POST":
            post_requests.append({
                "url": request.url,
                "method": request.method
            })
            # Log ALL POST requests for debugging (even excluded ones)
            url_lower = request.url.lower()
            excluded = ['google-analytics', 'googletagmanager', 'google.com', 'pagead', 'clarity', 'facebook', 'twitter', 'doubleclick', 'getnitropack', 'analytics', 'gtm', 'ccm']
            is_excluded = any(ex in url_lower for ex in excluded)
            
            # Try to capture form data
            try:
                post_data = request.post_data
                if post_data:
                    # Check if this looks like form data (check for form fields)
                    url_lower = request.url.lower()
                    is_form_domain = False
                    try:
                        from urllib.parse import urlparse
                        req_domain = urlparse(request.url).netloc
                        current_domain = urlparse(page.url).netloc if page.url else ""
                        form_domain = urlparse(form_action_url).netloc if form_action_url else ""
                        is_form_domain = (current_domain and req_domain == current_domain) or (form_domain and req_domain == form_domain)
                    except:
                        pass
                    
                    # Exclude CSS/JS files and other non-form resources FIRST
                    url_lower = request.url.lower()
                    excluded_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.ico', '.map']
                    excluded_paths = ['wp-includes', 'wp-content', '/static/', '/assets/', '/css/', '/js/', '/wp-json/', '/api/', '/dist/', '/build/']
                    is_excluded_resource = any(ext in url_lower for ext in excluded_extensions) or any(path in url_lower for path in excluded_paths)
                    
                    # If it's an excluded resource, skip immediately
                    if is_excluded_resource:
                        pass  # Don't capture this
                    else:
                        # Check if URL matches form action (exact match preferred)
                        url_matches_form = False
                        if form_action_url:
                            form_base = form_action_url.split('?')[0].rstrip('/')
                            req_base = request.url.split('?')[0].rstrip('/')
                            url_matches_form = req_base == form_base
                        
                        # Check if it's a form endpoint (but not a resource file)
                        is_form_endpoint = False
                        if not any(ext in url_lower for ext in excluded_extensions):
                            is_form_endpoint = any(kw in url_lower for kw in ['/contact', '/submit', '/form', '/message', '/send', '/mail'])
                        
                        # Check for form fields in POST data
                        has_form_fields = any(field in post_data.lower() for field in ['name=', 'email=', 'message=', 'subject=', 'phone=', 'wpforms', 'form[', 'contact', 'submit', 'g-recaptcha-response'])
                        
                        # Only capture if:
                        # 1. URL exactly matches form action OR
                        # 2. (Is form endpoint AND has form fields) OR
                        # 3. (Is form domain AND has form fields)
                        should_capture = url_matches_form or (is_form_endpoint and has_form_fields) or (is_form_domain and has_form_fields)
                        
                        if should_capture:
                            nonlocal form_submission_data
                            form_submission_data = {
                                "url": request.url,
                                "data_preview": post_data[:500] if len(post_data) > 500 else post_data,
                                "data_length": len(post_data)
                            }
                            ultra_safe_log_print(f"   📦 Form data detected in POST to {request.url[:80]}:")
                            ultra_safe_log_print(f"      {post_data[:300]}...")
            except:
                pass
            
            if is_excluded:
                ultra_safe_log_print(f"   ⏭️  POST request (EXCLUDED): {request.url[:100]}")
            else:
                ultra_safe_log_print(f"   📤 Form POST request: {request.url[:100]}")
        elif request.method == "GET" and contact_form_found:
            # Track GET requests for GET contact forms
            get_requests.append({
                "url": request.url,
                "method": request.method
            })
            # Check if this GET request matches form action
            try:
                from urllib.parse import urlparse, parse_qs
                req_domain = urlparse(request.url).netloc
                form_domain = urlparse(form_action_url).netloc if form_action_url else ""
                current_domain = urlparse(page.url).netloc if page.url else ""
                if (form_domain and req_domain == form_domain) or (current_domain and req_domain == current_domain):
                    # Check if URL contains form action path or query parameters (form data)
                    if form_action_url and (form_action_url.split('?')[0] in request.url or '?' in request.url):
                        # Extract and log query parameters (form data)
                        query_string = urlparse(request.url).query
                        if query_string:
                            try:
                                query_params = parse_qs(query_string)
                                ultra_safe_log_print(f"   📤 Form GET request: {request.url.split('?')[0]}")
                                ultra_safe_log_print(f"   📦 Form data in GET request:")
                                for key, values in query_params.items():
                                    value_preview = values[0][:100] if values and values[0] else '(empty)'
                                    ultra_safe_log_print(f"      - {key}: {value_preview}")
                                
                                # Store form submission data
                                form_submission_data = {
                                    "url": request.url,
                                    "method": "GET",
                                    "query_params": dict(query_params),
                                    "query_string": query_string[:500]
                                }
                            except:
                                ultra_safe_log_print(f"   📤 Form GET request: {request.url[:150]}")
                        else:
                            ultra_safe_log_print(f"   📤 Form GET request: {request.url[:100]}")
                        form_submission_detected = True
            except:
                pass
    
    def track_response(response):
        if response.request.method == "POST":
            post_responses.append({
                "url": response.url,
                "status": response.status
            })
            # Check if this is a form submission (not analytics/tracking)
            url_lower = response.url.lower()
            excluded = ['google-analytics', 'googletagmanager', 'google.com', 'pagead', 'clarity', 'facebook', 'twitter', 'doubleclick', 'getnitropack', 'analytics', 'gtm', 'ccm']
            
            # ALWAYS exclude Google/analytics domains first
            is_excluded = any(ex in url_lower for ex in excluded)
            if is_excluded:
                ultra_safe_log_print(f"   ⏭️  POST response (EXCLUDED): {response.status} - {response.url[:100]}")
                return  # Skip this response - it's analytics/tracking
            
            # Now check if it matches form action or current domain
            try:
                from urllib.parse import urlparse
                response_domain = urlparse(response.url).netloc
                form_domain = urlparse(form_action_url).netloc if form_action_url else ""
                current_domain = urlparse(page.url).netloc if page.url else ""
                
                # STRICT: Must match form domain or current domain (not external domains)
                is_form_submission = (
                    (form_domain and response_domain == form_domain) or
                    (current_domain and response_domain == current_domain)
                )
                
                # Also check URL path matches form action
                if not is_form_submission and form_action_url:
                    try:
                        form_path = urlparse(form_action_url).path
                        response_path = urlparse(response.url).path
                        if form_path and response_path.startswith(form_path):
                            is_form_submission = True
                    except:
                        pass
                
                if is_form_submission and response.status in [200, 201, 204, 302, 303]:
                    form_submission_detected = True
                    ultra_safe_log_print(f"   ✅ Form submission confirmed: {response.status} - {response.url[:80]}")
            except:
                # Fallback: if URL contains form-related keywords (but exclude analytics)
                if not any(ex in url_lower for ex in ['google.com', 'pagead', 'ccm', 'analytics']):
                    if any(kw in url_lower for kw in ['contact', 'submit', 'send', 'message']):
                        # Double-check domain matches
                        try:
                            from urllib.parse import urlparse
                            response_domain = urlparse(response.url).netloc
                            current_domain = urlparse(page.url).netloc if page.url else ""
                            if current_domain and response_domain == current_domain:
                                if response.status in [200, 201, 204, 302, 303]:
                                    form_submission_detected = True
                                    ultra_safe_log_print(f"   ✅ Form submission detected: {response.status}")
                        except:
                            pass
    
    
    # Set up tracking BEFORE attempting submission
    try:
        # Remove any existing listeners first
        page.remove_all_listeners("request")
        page.remove_all_listeners("response")
    except:
        pass
    
    # Track ALL requests to see what's happening
    all_requests = []
    def track_all_requests(request):
        all_requests.append({
            "url": request.url,
            "method": request.method
        })
        # Log all requests to the form domain
        try:
            from urllib.parse import urlparse
            req_domain = urlparse(request.url).netloc
            current_domain = urlparse(page.url).netloc if page.url else ""
            if current_domain and req_domain == current_domain and request.method == "POST":
                ultra_safe_log_print(f"   🔍 POST to same domain: {request.url[:100]}")
        except:
            pass
    
    try:
        page.on("request", track_request)
        page.on("request", track_all_requests)  # Also track all requests
        page.on("response", track_response)
        ultra_safe_log_print("   📡 POST request/response tracking enabled")
    except:
        pass
    
    # Also intercept fetch/XHR for AJAX form submissions
    # CRITICAL: Intercept and inject field values for React/Next.js forms
    try:
        await page.evaluate("""
            () => {
                window.__ajaxSubmissions = [];
                window.__formFieldValues = {};
                
                // Function to get all form field values from DOM (bypass React state)
                function getFormFieldValues() {
                    const form = document.querySelector('form');
                    if (!form) return {};
                    
                    const values = {};
                    const allFields = form.querySelectorAll('input, select, textarea');
                    allFields.forEach(field => {
                        if (field.type !== 'submit' && field.type !== 'button' && field.type !== 'hidden') {
                            const name = field.name || field.id || '';
                            if (name && field.value) {
                                values[name] = field.value;
                            }
                        }
                    });
                    return values;
                }
                
                // Function to inject WPForms fields into FormData
                function injectWPFormsFields(formData) {
                    if (!window.__wpformsData || !window.__wpformsData.is_wpforms) {
                        return formData;
                    }
                    
                    const wpforms = window.__wpformsData;
                    
                    // If it's FormData, append WPForms fields
                    if (formData instanceof FormData) {
                        if (wpforms.token) {
                            formData.set('wpforms[token]', wpforms.token);
                        }
                        if (wpforms.start_timestamp) {
                            formData.set('start_timestamp', wpforms.start_timestamp.toString());
                        }
                        if (wpforms.end_timestamp) {
                            formData.set('end_timestamp', wpforms.end_timestamp.toString());
                        }
                        if (wpforms.form_id) {
                            formData.set('wpforms[id]', wpforms.form_id);
                        }
                        if (wpforms.submit) {
                            formData.set('wpforms[submit]', wpforms.submit);
                        }
                        // Add action field for AJAX submission
                        if (wpforms.uses_ajax) {
                            formData.set('action', 'wpforms_submit');
                        }
                        // Inject other hidden fields
                        if (wpforms.hidden_fields) {
                            Object.keys(wpforms.hidden_fields).forEach(key => {
                                if (key && wpforms.hidden_fields[key]) {
                                    formData.set(key, wpforms.hidden_fields[key]);
                                }
                            });
                        }
                        return formData;
                    }
                    
                    // If it's a string (URL-encoded or multipart), append WPForms fields
                    if (typeof formData === 'string') {
                        const params = new URLSearchParams(formData);
                        if (wpforms.token) {
                            params.set('wpforms[token]', wpforms.token);
                        }
                        if (wpforms.start_timestamp) {
                            params.set('start_timestamp', wpforms.start_timestamp.toString());
                        }
                        if (wpforms.end_timestamp) {
                            params.set('end_timestamp', wpforms.end_timestamp.toString());
                        }
                        if (wpforms.form_id) {
                            params.set('wpforms[id]', wpforms.form_id);
                        }
                        if (wpforms.submit) {
                            params.set('wpforms[submit]', wpforms.submit);
                        }
                        // Inject other hidden fields
                        if (wpforms.hidden_fields) {
                            Object.keys(wpforms.hidden_fields).forEach(key => {
                                if (key && wpforms.hidden_fields[key]) {
                                    params.set(key, wpforms.hidden_fields[key]);
                                }
                            });
                        }
                        return params.toString();
                    }
                    
                    return formData;
                }
                
                // Function to inject field values into request body
                function injectFieldValues(body, fieldValues) {
                    if (!body) {
                        return body;
                    }
                    
                    // First, inject WPForms fields if available
                    if (window.__wpformsData && window.__wpformsData.is_wpforms) {
                        body = injectWPFormsFields(body);
                    }
                    
                    if (!fieldValues || Object.keys(fieldValues).length === 0) {
                        return body;
                    }
                    
                    try {
                        // Try to parse as JSON
                        if (typeof body === 'string' && body.trim().startsWith('{')) {
                            const data = JSON.parse(body);
                            // Merge field values into data
                            Object.keys(fieldValues).forEach(key => {
                                if (!data[key] || data[key] === '') {
                                    data[key] = fieldValues[key];
                                }
                            });
                            return JSON.stringify(data);
                        }
                    } catch (e) {
                        // Not JSON, might be FormData or URL-encoded
                    }
                    
                    return body;
                }
                
                // Intercept fetch
                const originalFetch = window.fetch;
                window.fetch = async function(...args) {
                    const url = args[0];
                    const options = args[1] || {};
                    if (options.method === 'POST' || options.method === 'post') {
                        // Get actual field values from DOM before submission
                        const fieldValues = getFormFieldValues();
                        window.__formFieldValues = fieldValues;
                        
                        // Inject WPForms fields and field values into request body
                        if (options.body) {
                            const originalBody = options.body;
                            const injectedBody = injectFieldValues(originalBody, fieldValues);
                            if (injectedBody !== originalBody) {
                                options.body = injectedBody;
                                if (window.__wpformsData && window.__wpformsData.is_wpforms) {
                                    console.log('🔧 Injected WPForms fields into fetch request');
                                } else {
                                    console.log('🔧 Injected field values into fetch request:', fieldValues);
                                }
                            }
                        } else {
                            // If no body, create one with field values
                            try {
                                options.body = JSON.stringify(fieldValues);
                                options.headers = options.headers || {};
                                options.headers['Content-Type'] = 'application/json';
                                console.log('🔧 Created request body with field values:', fieldValues);
                            } catch (e) {
                                console.log('⚠️ Could not create request body:', e);
                            }
                        }
                        
                        const submission = {
                            type: 'fetch',
                            url: url,
                            method: options.method || 'GET',
                            body: options.body ? (typeof options.body === 'string' ? options.body.substring(0, 500) : 'binary') : null,
                            field_values: fieldValues,
                            timestamp: Date.now()
                        };
                        window.__ajaxSubmissions.push(submission);
                        window.__formSubmissionDetected = true;
                        window.__formSubmissionURL = url;
                        console.log('🔍 AJAX fetch POST detected:', url, options);
                        
                        // Also capture response
                        try {
                            const response = await originalFetch.apply(this, args);
                            const clonedResponse = response.clone();
                            const responseData = await clonedResponse.text().catch(() => '');
                            submission.response_status = response.status;
                            submission.response_data = responseData.substring(0, 500);
                            if (response.status >= 200 && response.status < 300) {
                                submission.success = true;
                                window.__formSubmissionSuccess = true;
                            }
                            return response;
                        } catch (e) {
                            return originalFetch.apply(this, args);
                        }
                    }
                    return originalFetch.apply(this, args);
                };
                
                // Intercept XMLHttpRequest
                const originalOpen = XMLHttpRequest.prototype.open;
                const originalSend = XMLHttpRequest.prototype.send;
                XMLHttpRequest.prototype.open = function(method, url, ...rest) {
                    this._method = method;
                    this._url = url;
                    return originalOpen.apply(this, [method, url, ...rest]);
                };
                XMLHttpRequest.prototype.send = function(data) {
                    if (this._method === 'POST' || this._method === 'post') {
                        // Get actual field values from DOM before submission
                        const fieldValues = getFormFieldValues();
                        window.__formFieldValues = fieldValues;
                        
                        // Inject WPForms fields and field values into request data
                        let finalData = data;
                        if (data) {
                            finalData = injectFieldValues(data, fieldValues);
                            if (finalData !== data) {
                                if (window.__wpformsData && window.__wpformsData.is_wpforms) {
                                    console.log('🔧 Injected WPForms fields into XHR request');
                                } else {
                                    console.log('🔧 Injected field values into XHR request:', fieldValues);
                                }
                            }
                        } else {
                            // If no data, create it with field values
                            try {
                                finalData = JSON.stringify(fieldValues);
                                this.setRequestHeader('Content-Type', 'application/json');
                                console.log('🔧 Created XHR request data with field values:', fieldValues);
                            } catch (e) {
                                console.log('⚠️ Could not create XHR request data:', e);
                            }
                        }
                        
                        const submission = {
                            type: 'xhr',
                            url: this._url,
                            method: this._method,
                            data: finalData ? (typeof finalData === 'string' ? finalData.substring(0, 500) : 'binary') : null,
                            field_values: fieldValues,
                            timestamp: Date.now()
                        };
                        
                        // Capture response
                        this.addEventListener('load', function() {
                            submission.response_status = this.status;
                            submission.response_data = this.responseText ? this.responseText.substring(0, 500) : '';
                            if (this.status >= 200 && this.status < 300) {
                                submission.success = true;
                                window.__formSubmissionSuccess = true;
                            }
                        });
                        
                        window.__ajaxSubmissions.push(submission);
                        window.__formSubmissionDetected = true;
                        window.__formSubmissionURL = this._url;
                        console.log('🔍 AJAX XHR POST detected:', this._url, finalData ? finalData.substring(0, 100) : '');
                        
                        return originalSend.apply(this, [finalData]);
                    }
                    return originalSend.apply(this, [data]);
                };
            }
        """)
        ultra_safe_log_print("   📡 AJAX/fetch interception enabled")
    except:
        pass
    
    # Wait a moment for tracking to be set up
    await asyncio.sleep(1)
    
    # Check for Next.js form actions or other submission mechanisms
    form_action_info = await page.evaluate("""
        () => {
            // Get the target form (skip search forms)
            let form = null;
            if (typeof window.__targetFormIndex !== 'undefined' && window.__targetFormIndex !== null) {
                const allForms = Array.from(document.querySelectorAll('form'));
                const nonSearchForms = allForms.filter((f) => {
                    const method = (f.method || 'get').toLowerCase();
                    const role = f.getAttribute('role') || '';
                    const formText = f.textContent.toLowerCase();
                    const formId = (f.id || '').toLowerCase();
                    const formClass = (f.className || '').toLowerCase();
                    const action = f.action || '';
                    
                    const isSearch = role === 'search' || (method === 'get' && (
                        formText.includes('search') ||
                        formId.includes('search') ||
                        formClass.includes('search') ||
                        action.includes('search') ||
                        f.querySelector('input[type="search"]') ||
                        f.querySelector('input[name*="search"]') ||
                        f.querySelector('input[name*="q"]') ||
                        f.querySelector('input[name="s"]')
                    ));
                    
                    return !isSearch;
                });
                
                if (nonSearchForms.length > window.__targetFormIndex) {
                    form = nonSearchForms[window.__targetFormIndex];
                }
            }
            
            // Fallback to first non-search form
            if (!form) {
                const allForms = Array.from(document.querySelectorAll('form'));
                const nonSearchForms = allForms.filter((f) => {
                    const method = (f.method || 'get').toLowerCase();
                    const role = f.getAttribute('role') || '';
                    return role !== 'search' && !(method === 'get' && (
                        f.textContent.toLowerCase().includes('search') ||
                        f.className.toLowerCase().includes('search') ||
                        f.querySelector('input[type="search"]')
                    ));
                });
                if (nonSearchForms.length > 0) {
                    form = nonSearchForms[0];
                } else {
                    form = document.querySelector('form');
                }
            }
            
            if (!form) return { has_form: false };
            
            const action = form.getAttribute('action') || '';
            const method = (form.getAttribute('method') || 'get').toLowerCase();
            const onSubmit = form.getAttribute('onsubmit') || '';
            const hasAction = form.hasAttribute('action');
            
            // Check for Next.js form action
            const formAction = form.getAttribute('action') || '';
            const isNextJSForm = formAction.includes('/api/') || formAction.includes('?/') || !hasAction;
            
            // Check submit button for formAction
            const submitBtn = form.querySelector('button[type="submit"]');
            const btnFormAction = submitBtn ? submitBtn.getAttribute('formAction') : null;
            
            return {
                has_form: true,
                action: action,
                method: method,
                hasAction: hasAction,
                isNextJSForm: isNextJSForm,
                btnFormAction: btnFormAction,
                onSubmit: onSubmit ? 'present' : 'none'
            };
        }
    """)
    
    if form_action_info.get('has_form'):
        ultra_safe_log_print(f"   📋 Form submission info:")
        ultra_safe_log_print(f"      Action: {form_action_info.get('action', 'none')[:80]}")
        ultra_safe_log_print(f"      Method: {form_action_info.get('method', 'get').upper()}")
        if form_action_info.get('isNextJSForm'):
            ultra_safe_log_print(f"      ⚠️  Next.js form detected - may use Server Actions")
        if form_action_info.get('btnFormAction'):
            ultra_safe_log_print(f"      Button formAction: {form_action_info.get('btnFormAction')[:80]}")
    
    # Verify form fields before submission
    try:
        form_verification = await page.evaluate("""
            () => {
                // Get the target form (skip search forms)
                let form = null;
                if (typeof window.__targetFormIndex !== 'undefined' && window.__targetFormIndex !== null) {
                    const allForms = Array.from(document.querySelectorAll('form'));
                    const nonSearchForms = allForms.filter((f) => {
                        const method = (f.method || 'get').toLowerCase();
                        const role = f.getAttribute('role') || '';
                        const formText = f.textContent.toLowerCase();
                        const formId = (f.id || '').toLowerCase();
                        const formClass = (f.className || '').toLowerCase();
                        const action = f.action || '';
                        
                        const isSearch = role === 'search' || (method === 'get' && (
                            formText.includes('search') ||
                            formId.includes('search') ||
                            formClass.includes('search') ||
                            action.includes('search') ||
                            f.querySelector('input[type="search"]') ||
                            f.querySelector('input[name*="search"]') ||
                            f.querySelector('input[name*="q"]') ||
                            f.querySelector('input[name="s"]')
                        ));
                        
                        return !isSearch;
                    });
                    
                    if (nonSearchForms.length > window.__targetFormIndex) {
                        form = nonSearchForms[window.__targetFormIndex];
                    }
                }
                
                // Fallback to first non-search form
                if (!form) {
                    const allForms = Array.from(document.querySelectorAll('form'));
                    const nonSearchForms = allForms.filter((f) => {
                        const method = (f.method || 'get').toLowerCase();
                        const role = f.getAttribute('role') || '';
                        return role !== 'search' && !(method === 'get' && (
                            f.textContent.toLowerCase().includes('search') ||
                            f.className.toLowerCase().includes('search') ||
                            f.querySelector('input[type="search"]')
                        ));
                    });
                    if (nonSearchForms.length > 0) {
                        form = nonSearchForms[0];
                    } else {
                        form = document.querySelector('form');
                    }
                }
                
                if (!form) return { found: false };
                
                const fields = {
                    inputs: [],
                    selects: [],
                    textareas: [],
                    checkboxes: [],
                    required_empty: []
                };
                
                // Check all inputs
                form.querySelectorAll('input').forEach(input => {
                    if (input.type === 'checkbox') {
                        fields.checkboxes.push({
                            name: input.name || input.id,
                            checked: input.checked,
                            required: input.required
                        });
                    } else if (input.type !== 'submit' && input.type !== 'button' && input.type !== 'hidden') {
                        fields.inputs.push({
                            name: input.name || input.id,
                            value: input.value,
                            required: input.required,
                            empty: !input.value || input.value.trim() === ''
                        });
                        if (input.required && (!input.value || input.value.trim() === '')) {
                            fields.required_empty.push(input.name || input.id || 'unnamed');
                        }
                    }
                });
                
                // Check selects
                form.querySelectorAll('select').forEach(select => {
                    fields.selects.push({
                        name: select.name || select.id,
                        value: select.value,
                        required: select.required,
                        empty: !select.value || select.value === ''
                    });
                    if (select.required && (!select.value || select.value === '')) {
                        fields.required_empty.push(select.name || select.id || 'unnamed');
                    }
                });
                
                // Check textareas
                form.querySelectorAll('textarea').forEach(textarea => {
                    fields.textareas.push({
                        name: textarea.name || textarea.id,
                        value: textarea.value,
                        required: textarea.required,
                        empty: !textarea.value || textarea.value.trim() === ''
                    });
                    if (textarea.required && (!textarea.value || textarea.value.trim() === '')) {
                        fields.required_empty.push(textarea.name || textarea.id || 'unnamed');
                    }
                });
                
                return {
                    found: true,
                    action: form.action || window.location.href,
                    method: form.method || 'get',
                    fields: fields,
                    required_empty: fields.required_empty
                };
            }
        """)
        
        if form_verification.get('found'):
            ultra_safe_log_print(f"   🔍 Form verification:")
            ultra_safe_log_print(f"      Action: {form_verification.get('action', 'N/A')[:80]}")
            ultra_safe_log_print(f"      Method: {form_verification.get('method', 'N/A').upper()}")
            ultra_safe_log_print(f"      Inputs: {len(form_verification.get('fields', {}).get('inputs', []))}")
            ultra_safe_log_print(f"      Selects: {len(form_verification.get('fields', {}).get('selects', []))}")
            ultra_safe_log_print(f"      Textareas: {len(form_verification.get('fields', {}).get('textareas', []))}")
            ultra_safe_log_print(f"      Checkboxes: {len(form_verification.get('fields', {}).get('checkboxes', []))}")
            required_empty = form_verification.get('required_empty', [])
            if required_empty:
                ultra_safe_log_print(f"      ⚠️  Required fields empty: {', '.join(required_empty)}")
            else:
                ultra_safe_log_print(f"      ✅ All required fields filled")
            
            # Allow GET forms if they're contact forms
            form_method = form_verification.get('method', 'get').lower()
            form_method = form_method  # Store for later use
            if form_method == 'get' and not contact_form_found:
                ultra_safe_log_print("   ⏭️  Skipping GET form (not a contact form)")
                result["submission_attempted"] = False
                result["submission_success"] = False
                return result
            elif form_method == 'get' and contact_form_found:
                ultra_safe_log_print("   ℹ️  Contact form uses GET method - will track GET requests")
                form_method = "GET"  # Update global form_method
    except Exception as e:
        ultra_safe_log_print(f"   ⚠️  Form verification failed: {str(e)[:50]}")
    
    # Try to find and click submit button properly
    submit_button_found = False
    try:
        # Try multiple selectors for submit button
        submit_selectors = [
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("Submit")',
            'button:has-text("Send")',
            'form button:last-child',
            'form button'
        ]
        
        for selector in submit_selectors:
            try:
                submit_btn = await page.query_selector(selector)
                if submit_btn:
                    submit_button_found = True
                    ultra_safe_log_print(f"   ✅ Submit button found: {selector}")
                    
                    # Scroll into view
                    await submit_btn.scroll_into_view_if_needed()
                    await asyncio.sleep(0.5)
                    
                    # Check if CAPTCHA is solved before submission
                    captcha_check = await page.evaluate("""
                        () => {
                            // Check for reCAPTCHA response
                            const recaptchaResponse = document.querySelector('#g-recaptcha-response');
                            const hasRecaptchaResponse = recaptchaResponse && recaptchaResponse.value && recaptchaResponse.value.length > 0;
                            
                            // Check for hCaptcha response
                            const hcaptchaResponse = document.querySelector('[name="h-captcha-response"]');
                            const hasHcaptchaResponse = hcaptchaResponse && hcaptchaResponse.value && hcaptchaResponse.value.length > 0;
                            
                            // Check if CAPTCHA widget/iframe is present
                            const captchaWidget = document.querySelector('.g-recaptcha, [data-sitekey], .h-captcha, .captcha-widget, .captcha-container');
                            const hasCaptchaWidget = captchaWidget && captchaWidget.offsetParent !== null;
                            
                            // Check for reCAPTCHA iframe
                            const recaptchaIframe = document.querySelector('iframe[title*="reCAPTCHA"], iframe[src*="recaptcha"]');
                            const hasRecaptchaIframe = recaptchaIframe && recaptchaIframe.offsetParent !== null;
                            
                            // Check for hCaptcha iframe
                            const hcaptchaIframe = document.querySelector('iframe[src*="hcaptcha"]');
                            const hasHcaptchaIframe = hcaptchaIframe && hcaptchaIframe.offsetParent !== null;
                            
                            const hasCaptcha = hasCaptchaWidget || hasRecaptchaIframe || hasHcaptchaIframe;
                            const isSolved = hasRecaptchaResponse || hasHcaptchaResponse;
                            
                            return {
                                hasCaptcha: hasCaptcha,
                                isSolved: isSolved,
                                hasRecaptchaResponse: hasRecaptchaResponse,
                                hasHcaptchaResponse: hasHcaptchaResponse,
                                hasRecaptchaIframe: hasRecaptchaIframe,
                                hasHcaptchaIframe: hasHcaptchaIframe
                            };
                        }
                    """)
                    
                    captcha_solved = captcha_check.get('isSolved', False)
                    has_captcha = captcha_check.get('hasCaptcha', False)
                    
                    if has_captcha:
                        ultra_safe_log_print(f"   🔍 CAPTCHA detected: reCAPTCHA iframe={captcha_check.get('hasRecaptchaIframe')}, hCaptcha iframe={captcha_check.get('hasHcaptchaIframe')}")
                        ultra_safe_log_print(f"   🔍 CAPTCHA status: solved={captcha_solved}, response present={captcha_check.get('hasRecaptchaResponse') or captcha_check.get('hasHcaptchaResponse')}")
                    
                    if not captcha_solved:
                        ultra_safe_log_print("   ⚠️  CAPTCHA not solved yet, attempting to solve (with timeout)...")
                        # Try to solve CAPTCHA using the solver with timeout to prevent hanging
                        try:
                            # Validate page is still open
                            if page.is_closed():
                                ultra_safe_log_print("   ⚠️  Page is closed, skipping CAPTCHA solving")
                            else:
                                solver = LocalCaptchaSolver(page=page)
                                # Set a short timeout for CAPTCHA solving (10 seconds max)
                                try:
                                    solution = await asyncio.wait_for(
                                        solver.detect_and_solve_captcha(page),
                                        timeout=10.0
                                    )
                                    if solution and solution.get("solved"):
                                        # Validate page is still open before injection
                                        if not page.is_closed():
                                            injected = await solver.inject_captcha_solution(page, solution)
                                            if injected:
                                                ultra_safe_log_print("   ✅ CAPTCHA solved before submission")
                                                await asyncio.sleep(2)  # Wait for CAPTCHA to be processed
                                                
                                                # Verify CAPTCHA response is now present
                                                if not page.is_closed():
                                                    captcha_verified = await page.evaluate("""
                                                        () => {
                                                            const recaptchaResponse = document.querySelector('#g-recaptcha-response');
                                                            return recaptchaResponse && recaptchaResponse.value && recaptchaResponse.value.length > 0;
                                                        }
                                                    """)
                                                    if captcha_verified:
                                                        ultra_safe_log_print("   ✅ CAPTCHA response verified in form")
                                                    else:
                                                        ultra_safe_log_print("   ⚠️  CAPTCHA response not found in form after injection")
                                            else:
                                                ultra_safe_log_print("   ⚠️  CAPTCHA solved but injection failed")
                                        else:
                                            ultra_safe_log_print("   ⚠️  Page closed during CAPTCHA injection")
                                    else:
                                        ultra_safe_log_print("   ⚠️  Could not solve CAPTCHA (will proceed with submission anyway)")
                                except asyncio.TimeoutError:
                                    ultra_safe_log_print("   ⚠️  CAPTCHA solving timed out (10s), proceeding with submission anyway")
                                except Exception as solve_error:
                                    error_msg = str(solve_error)
                                    # Check if page closed
                                    try:
                                        if page.is_closed():
                                            ultra_safe_log_print("   ⚠️  Page closed during CAPTCHA solving")
                                        else:
                                            ultra_safe_log_print(f"   ⚠️  CAPTCHA solving failed: {error_msg[:50]}")
                                    except:
                                        ultra_safe_log_print("   ⚠️  CAPTCHA solving failed (page may be closed)")
                        except Exception as e:
                            ultra_safe_log_print(f"   ⚠️  CAPTCHA solving error: {str(e)[:50]}")
                            ultra_safe_log_print("   ℹ️  Proceeding with form submission anyway")
                    else:
                        ultra_safe_log_print("   ✅ CAPTCHA is solved or not present")
                    
                    # Verify CAPTCHA token is actually present and valid-looking
                    captcha_token_check = await page.evaluate("""
                        () => {
                            const recaptchaResponse = document.querySelector('#g-recaptcha-response');
                            if (recaptchaResponse && recaptchaResponse.value) {
                                const token = recaptchaResponse.value;
                                // Check if token looks valid (not empty, has reasonable length)
                                if (token.length > 20 && token.startsWith('03AOLTBLR_')) {
                                    return { valid: true, token_length: token.length };
                                }
                                return { valid: false, reason: 'Token format invalid' };
                            }
                            return { valid: false, reason: 'No token found' };
                        }
                    """)
                    
                    if not captcha_token_check.get('valid'):
                        ultra_safe_log_print(f"   ⚠️  CAPTCHA token validation failed: {captcha_token_check.get('reason')}")
                        ultra_safe_log_print("   🔄 Attempting to solve CAPTCHA again (with timeout)...")
                        try:
                            # Validate page is still open
                            if page.is_closed():
                                ultra_safe_log_print("   ⚠️  Page is closed, skipping CAPTCHA re-solving")
                            else:
                                solver = LocalCaptchaSolver(page=page)
                                # Set a short timeout (5 seconds max) for re-solving
                                try:
                                    solution = await asyncio.wait_for(
                                        solver.detect_and_solve_captcha(page),
                                        timeout=5.0
                                    )
                                    if solution and solution.get("solved"):
                                        # Validate page is still open before injection
                                        if not page.is_closed():
                                            injected = await solver.inject_captcha_solution(page, solution)
                                            if injected:
                                                ultra_safe_log_print("   ✅ CAPTCHA re-solved and injected")
                                                await asyncio.sleep(2)
                                        else:
                                            ultra_safe_log_print("   ⚠️  Page closed during CAPTCHA re-solving")
                                    else:
                                        ultra_safe_log_print("   ⚠️  CAPTCHA re-solving failed (will proceed anyway)")
                                except asyncio.TimeoutError:
                                    ultra_safe_log_print("   ⚠️  CAPTCHA re-solving timed out (5s), proceeding with submission")
                                except Exception as re_solve_error:
                                    error_msg = str(re_solve_error)
                                    try:
                                        if page.is_closed():
                                            ultra_safe_log_print("   ⚠️  Page closed during CAPTCHA re-solving")
                                        else:
                                            ultra_safe_log_print(f"   ⚠️  CAPTCHA re-solving failed: {error_msg[:50]}")
                                    except:
                                        ultra_safe_log_print("   ⚠️  CAPTCHA re-solving failed")
                        except Exception as e:
                            ultra_safe_log_print(f"   ⚠️  CAPTCHA re-solving error: {str(e)[:50]}")
                            ultra_safe_log_print("   ℹ️  Proceeding with form submission anyway")
                    else:
                        ultra_safe_log_print(f"   ✅ CAPTCHA token validated (length: {captcha_token_check.get('token_length')})")
                    
                    # Final check: verify all required fields including CAPTCHA
                    final_form_check = await page.evaluate("""
                        () => {
                            const form = document.querySelector('form');
                            if (!form) return { ready: false, issues: [] };
                            
                            const issues = [];
                            const allFields = form.querySelectorAll('input, select, textarea');
                            
                            allFields.forEach(field => {
                                if (field.required && field.type !== 'submit' && field.type !== 'button' && field.type !== 'hidden') {
                                    const isEmpty = !field.value || field.value.trim() === '' || 
                                                  (field.type === 'checkbox' && !field.checked);
                                    if (isEmpty) {
                                        issues.push(`Required field '${field.name || field.id}' is empty`);
                                    }
                                }
                            });
                            
                            // Check CAPTCHA
                            const recaptchaResponse = document.querySelector('#g-recaptcha-response');
                            if (recaptchaResponse && !recaptchaResponse.value) {
                                const captchaWidget = document.querySelector('.g-recaptcha, [data-sitekey]');
                                if (captchaWidget && captchaWidget.offsetParent !== null) {
                                    issues.push('CAPTCHA is required but not solved');
                                }
                            }
                            
                            return {
                                ready: issues.length === 0,
                                issues: issues
                            };
                        }
                    """)
                    
                    if not final_form_check.get('ready'):
                        issues = final_form_check.get('issues', [])
                        ultra_safe_log_print(f"   ⚠️  Form not ready for submission:")
                        for issue in issues:
                            ultra_safe_log_print(f"      - {issue}")
                        
                        # If CAPTCHA is the only issue, try to solve it one more time (with very short timeout)
                        if len(issues) == 1 and 'CAPTCHA' in issues[0]:
                            ultra_safe_log_print("   🔄 Attempting to solve CAPTCHA one more time (with timeout)...")
                            try:
                                # Validate page is still open
                                if page.is_closed():
                                    ultra_safe_log_print("   ⚠️  Page is closed, skipping final CAPTCHA attempt")
                                else:
                                    solver = LocalCaptchaSolver(page=page)
                                    # Set a very short timeout (3 seconds max) for final attempt
                                    try:
                                        solution = await asyncio.wait_for(
                                            solver.detect_and_solve_captcha(page),
                                            timeout=3.0
                                        )
                                        if solution and solution.get("solved"):
                                            if not page.is_closed():
                                                injected = await solver.inject_captcha_solution(page, solution)
                                                if injected:
                                                    ultra_safe_log_print("   ✅ CAPTCHA solved")
                                                    await asyncio.sleep(2)
                                    except asyncio.TimeoutError:
                                        ultra_safe_log_print("   ⚠️  Final CAPTCHA attempt timed out (3s), proceeding with submission")
                                    except Exception as final_error:
                                        try:
                                            if page.is_closed():
                                                ultra_safe_log_print("   ⚠️  Page closed during final CAPTCHA attempt")
                                            else:
                                                ultra_safe_log_print(f"   ⚠️  Final CAPTCHA attempt failed: {str(final_error)[:50]}")
                                        except:
                                            pass
                            except Exception as e:
                                ultra_safe_log_print(f"   ⚠️  Final CAPTCHA attempt error: {str(e)[:50]}")
                                ultra_safe_log_print("   ℹ️  Proceeding with form submission anyway")
                    
                    # Get the target form element (skip search forms)
                    target_form_element = None
                    if target_form is not None:
                        # Get the specific form by index
                        target_form_element = await page.evaluate(f"""
                            () => {{
                                const allForms = Array.from(document.querySelectorAll('form'));
                                const searchForms = allForms.filter((form, index) => {{
                                    const method = (form.method || 'get').toLowerCase();
                                    const role = form.getAttribute('role') || '';
                                    const formText = form.textContent.toLowerCase();
                                    const formId = (form.id || '').toLowerCase();
                                    const formClass = (form.className || '').toLowerCase();
                                    const action = form.action || '';
                                    
                                    return role === 'search' || (method === 'get' && (
                                        formText.includes('search') ||
                                        formId.includes('search') ||
                                        formClass.includes('search') ||
                                        action.includes('search') ||
                                        form.querySelector('input[type="search"]') ||
                                        form.querySelector('input[name*="search"]') ||
                                        form.querySelector('input[name*="q"]') ||
                                        form.querySelector('input[name="s"]')
                                    ));
                                }});
                                
                                // Filter out search forms
                                const nonSearchForms = allForms.filter((form, index) => {{
                                    const method = (form.method || 'get').toLowerCase();
                                    const role = form.getAttribute('role') || '';
                                    const formText = form.textContent.toLowerCase();
                                    const formId = (form.id || '').toLowerCase();
                                    const formClass = (form.className || '').toLowerCase();
                                    const action = form.action || '';
                                    
                                    const isSearch = role === 'search' || (method === 'get' && (
                                        formText.includes('search') ||
                                        formId.includes('search') ||
                                        formClass.includes('search') ||
                                        action.includes('search') ||
                                        form.querySelector('input[type="search"]') ||
                                        form.querySelector('input[name*="search"]') ||
                                        form.querySelector('input[name*="q"]') ||
                                        form.querySelector('input[name="s"]')
                                    ));
                                    
                                    return !isSearch;
                                }});
                                
                                if (nonSearchForms.length > {target_form}) {{
                                    return nonSearchForms[{target_form}];
                                }}
                                return null;
                            }}
                        """)
                    
                    # Check if this is WPForms with AJAX - submit via AJAX instead
                    wpforms_ajax_check = await page.evaluate("""
                        () => {
                            if (window.__wpformsData && window.__wpformsData.is_wpforms && window.__wpformsData.uses_ajax) {
                                return {
                                    is_wpforms_ajax: true,
                                    ajax_url: window.__wpformsData.ajax_url || '/wp-admin/admin-ajax.php'
                                };
                            }
                            return { is_wpforms_ajax: false };
                        }
                    """)
                    
                    if wpforms_ajax_check.get('is_wpforms_ajax'):
                        ultra_safe_log_print("   🔑 WPForms AJAX detected - submitting via AJAX endpoint")
                        ajax_url = wpforms_ajax_check.get('ajax_url', '/wp-admin/admin-ajax.php')
                        
                        # Build absolute URL
                        from urllib.parse import urljoin
                        absolute_ajax_url = urljoin(page.url, ajax_url)
                        ultra_safe_log_print(f"   📤 AJAX URL: {absolute_ajax_url}")
                        
                        # Submit via AJAX using fetch
                        ajax_result = await page.evaluate("""
                            async (ajaxUrl) => {
                                try {
                                    const form = document.querySelector('form.wpforms-form, form[data-formid]');
                                    if (!form) {
                                        return { success: false, error: 'Form not found' };
                                    }
                                    
                                    // Build FormData from form
                                    const formData = new FormData(form);
                                    
                                    // Ensure all WPForms fields are included
                                    if (window.__wpformsData) {
                                        const wpforms = window.__wpformsData;
                                        if (wpforms.token) {
                                            formData.set('wpforms[token]', wpforms.token);
                                        }
                                        if (wpforms.start_timestamp) {
                                            formData.set('start_timestamp', wpforms.start_timestamp.toString());
                                        }
                                        if (wpforms.end_timestamp) {
                                            formData.set('end_timestamp', wpforms.end_timestamp.toString());
                                        }
                                        if (wpforms.form_id) {
                                            formData.set('wpforms[id]', wpforms.form_id);
                                        }
                                        formData.set('wpforms[submit]', 'wpforms-submit');
                                        formData.set('action', 'wpforms_submit');
                                    }
                                    
                                    // Submit via fetch
                                    const response = await fetch(ajaxUrl, {
                                        method: 'POST',
                                        body: formData,
                                        credentials: 'same-origin'
                                    });
                                    
                                    const responseText = await response.text();
                                    
                                    return {
                                        success: response.ok,
                                        status: response.status,
                                        response: responseText.substring(0, 500)
                                    };
                                } catch (e) {
                                    return { success: false, error: e.message };
                                }
                            }
                        """, absolute_ajax_url)
                        
                        if ajax_result.get('success'):
                            ultra_safe_log_print(f"   ✅ WPForms AJAX submission successful: {ajax_result.get('status')}")
                            result["submission_attempted"] = True
                            result["submission_success"] = True
                            result["method_used"] = "wpforms_ajax"
                            result["form_submission_detected"] = True
                        else:
                            ultra_safe_log_print(f"   ⚠️  WPForms AJAX submission failed: {ajax_result.get('error', 'Unknown error')}")
                            # Fall through to regular button click
                            result["submission_attempted"] = True
                            result["method_used"] = "button_click"
                            ultra_safe_log_print("   📤 Falling back to button click...")
                    else:
                        # Don't clear - we want to track the POST/GET
                        result["submission_attempted"] = True
                        result["method_used"] = "button_click"
                        ultra_safe_log_print("   📤 Submitting form...")
                        
                        # Always click submit button at least once, even if CAPTCHA solving failed
                        try:
                            # Find submit button in the target form (skip search forms)
                            submit_button = None
                            if target_form is not None:
                                # Build selector for the target form
                                form_selector = await page.evaluate(f"""
                                    () => {{
                                        const allForms = Array.from(document.querySelectorAll('form'));
                                        const nonSearchForms = allForms.filter((f) => {{
                                            const method = (f.method || 'get').toLowerCase();
                                            const role = f.getAttribute('role') || '';
                                            const formText = f.textContent.toLowerCase();
                                            const formId = (f.id || '').toLowerCase();
                                            const formClass = (f.className || '').toLowerCase();
                                            const action = f.action || '';
                                            
                                            const isSearch = role === 'search' || (method === 'get' && (
                                                formText.includes('search') ||
                                                formId.includes('search') ||
                                                formClass.includes('search') ||
                                                action.includes('search') ||
                                                f.querySelector('input[type="search"]') ||
                                                f.querySelector('input[name*="search"]') ||
                                                f.querySelector('input[name*="q"]') ||
                                                f.querySelector('input[name="s"]')
                                            ));
                                            
                                            return !isSearch;
                                        }});
                                        
                                        if (nonSearchForms.length > {target_form}) {{
                                            const targetForm = nonSearchForms[{target_form}];
                                            if (targetForm.id) {{
                                                return `#${{targetForm.id}} button[type="submit"], #${{targetForm.id}} input[type="submit"]`;
                                            }} else if (targetForm.className) {{
                                                const classes = targetForm.className.split(' ').filter(c => c).join('.');
                                                return `form.${{classes}} button[type="submit"], form.${{classes}} input[type="submit"]`;
                                            }} else {{
                                                const formIndex = Array.from(document.querySelectorAll('form')).indexOf(targetForm);
                                                return `form:nth-of-type(${{formIndex + 1}}) button[type="submit"], form:nth-of-type(${{formIndex + 1}}) input[type="submit"]`;
                                            }}
                                        }}
                                        return null;
                                    }}
                                """)
                                
                                if form_selector:
                                    submit_button = await page.query_selector(form_selector)
                            
                            # If still no button found, try to find any submit button (but skip search forms)
                            if not submit_button:
                                submit_button = await page.query_selector('form:not([role="search"]) button[type="submit"], form:not([role="search"]) input[type="submit"], button:has-text("Submit"), button:has-text("Send")')
                            
                            # If still no button found, try to find any submit button
                            if not submit_button:
                                submit_button = await page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Send"), form button:not([type="button"])')
                            
                            if submit_button:
                                ultra_safe_log_print("   ✅ Submit button found, clicking...")
                                try:
                                    await submit_button.click(timeout=10000)
                                    ultra_safe_log_print("   ✅ Submit button clicked")
                                    result["submission_attempted"] = True
                                    await asyncio.sleep(2)  # Wait for submission to process
                                except Exception as click_error:
                                    ultra_safe_log_print(f"   ⚠️  Submit button click failed: {str(click_error)[:50]}")
                                    # Try JavaScript click as fallback
                                    try:
                                        await submit_button.evaluate("(btn) => btn.click()")
                                        ultra_safe_log_print("   ✅ Submit button clicked via JavaScript")
                                        result["submission_attempted"] = True
                                        await asyncio.sleep(2)
                                    except:
                                        ultra_safe_log_print("   ⚠️  JavaScript click also failed")
                            else:
                                ultra_safe_log_print("   ⚠️  Submit button not found, trying form.submit()...")
                                # Fallback to form.submit()
                                try:
                                    await page.evaluate("() => { const form = document.querySelector('form'); if (form) form.submit(); }")
                                    ultra_safe_log_print("   ✅ Form submitted via form.submit()")
                                    result["submission_attempted"] = True
                                    await asyncio.sleep(2)
                                except Exception as submit_error:
                                    ultra_safe_log_print(f"   ⚠️  form.submit() failed: {str(submit_error)[:50]}")
                        except Exception as e:
                            ultra_safe_log_print(f"   ⚠️  Form submission error: {str(e)[:50]}")
                            result["submission_attempted"] = True  # Mark as attempted even if it failed
                    
                    # For GET forms, ensure all fields have names and construct URL if needed
                    if form_method == "GET" or form_method == "get":
                        try:
                            # Check if all fields have names
                            form_data_check = await page.evaluate("""
                                () => {
                                    const form = document.querySelector('form');
                                    if (!form) return { has_form: false };
                                    
                                    const fields_without_names = [];
                                    const form_data = new URLSearchParams();
                                    
                                    const allFields = form.querySelectorAll('input, select, textarea');
                                    allFields.forEach(field => {
                                        if (field.type === 'submit' || field.type === 'button' || field.type === 'hidden') {
                                            return;
                                        }
                                        
                                        const fieldName = field.name || field.id;
                                        if (!fieldName) {
                                            fields_without_names.push({
                                                type: field.type || field.tagName.toLowerCase(),
                                                placeholder: field.placeholder || ''
                                            });
                                        } else if (field.value) {
                                            if (field.type === 'checkbox' || field.type === 'radio') {
                                                if (field.checked) {
                                                    form_data.append(fieldName, field.value || 'on');
                                                }
                                            } else {
                                                form_data.append(fieldName, field.value);
                                            }
                                        }
                                    });
                                    
                                    return {
                                        has_form: true,
                                        fields_without_names: fields_without_names,
                                        form_data_string: form_data.toString(),
                                        will_include_data: form_data.toString().length > 0
                                    };
                                }
                            """)
                            
                            if form_data_check.get('has_form'):
                                fields_without_names = form_data_check.get('fields_without_names', [])
                                if fields_without_names:
                                    ultra_safe_log_print(f"   ⚠️  Found {len(fields_without_names)} field(s) without names - they won't be submitted!")
                                
                                form_data_string = form_data_check.get('form_data_string', '')
                                if not form_data_check.get('will_include_data'):
                                    ultra_safe_log_print("   ⚠️  No form data will be included in GET request!")
                                    ultra_safe_log_print("   🔧 Attempting to fix field names...")
                                    
                                    # Try to add names to fields
                                    await page.evaluate("""
                                        () => {
                                            const form = document.querySelector('form');
                                            if (!form) return;
                                            
                                            const fields = form.querySelectorAll('input, select, textarea');
                                            fields.forEach((field, index) => {
                                                if (!field.name && !field.id && field.type !== 'submit' && field.type !== 'button' && field.type !== 'hidden') {
                                                    const placeholder = (field.placeholder || '').toLowerCase();
                                                    if (field.type === 'email' || placeholder.includes('email')) {
                                                        field.name = 'email';
                                                    } else if (placeholder.includes('name')) {
                                                        field.name = 'name';
                                                    } else if (placeholder.includes('phone') || field.type === 'tel') {
                                                        field.name = 'phone';
                                                    } else if (placeholder.includes('message') || field.tagName === 'TEXTAREA') {
                                                        field.name = 'message';
                                                    } else {
                                                        field.name = 'field_' + index;
                                                    }
                                                }
                                            });
                                        }
                                    """)
                                    
                                    # Re-check form data
                                    form_data_check = await page.evaluate("""
                                        () => {
                                            const form = document.querySelector('form');
                                            if (!form) return { form_data_string: '' };
                                            
                                            const form_data = new URLSearchParams();
                                            const allFields = form.querySelectorAll('input, select, textarea');
                                            allFields.forEach(field => {
                                                if (field.type === 'submit' || field.type === 'button' || field.type === 'hidden') {
                                                    return;
                                                }
                                                
                                                const fieldName = field.name || field.id;
                                                if (fieldName && field.value) {
                                                    if (field.type === 'checkbox' || field.type === 'radio') {
                                                        if (field.checked) {
                                                            form_data.append(fieldName, field.value || 'on');
                                                        }
                                                    } else {
                                                        form_data.append(fieldName, field.value);
                                                    }
                                                }
                                            });
                                            
                                            return { form_data_string: form_data.toString() };
                                        }
                                    """)
                                    form_data_string = form_data_check.get('form_data_string', '')
                                
                                if form_data_string:
                                    ultra_safe_log_print(f"   ✅ Form data to be submitted: {form_data_string[:200]}")
                                else:
                                    ultra_safe_log_print("   ⚠️  Still no form data - form may not submit correctly")
                            
                            # For GET forms, always try button click first (many modern forms use JavaScript)
                            # But first, ensure all field values are properly set (especially for React/Next.js)
                            ultra_safe_log_print("   🔧 Ensuring all field values are set before submission...")
                            
                            # CRITICAL: For React/Next.js forms, we need to update React's internal state
                            # and intercept the form submission to ensure field values are included
                            await page.evaluate("""
                                () => {
                                    const form = document.querySelector('form');
                                    if (!form) return;
                                    
                                    // Store original field values before React might clear them
                                    window.__formFieldValues = {};
                                    const allFields = form.querySelectorAll('input, select, textarea');
                                    allFields.forEach(field => {
                                        if (field.type !== 'submit' && field.type !== 'button' && field.type !== 'hidden') {
                                            const fieldName = field.name || field.id || '';
                                            if (field.value && fieldName) {
                                                window.__formFieldValues[fieldName] = field.value;
                                            }
                                        }
                                    });
                                    
                                    // For React/Next.js controlled components, we need to trigger React's synthetic events
                                    allFields.forEach(field => {
                                        if (field.type !== 'submit' && field.type !== 'button' && field.type !== 'hidden') {
                                            if (field.value) {
                                                // Get the native value setter
                                                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value")?.set;
                                                const nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value")?.set;
                                                
                                                // Use native setter to update value (bypasses React's restrictions)
                                                if (field.tagName === 'INPUT' && nativeInputValueSetter) {
                                                    nativeInputValueSetter.call(field, field.value);
                                                } else if (field.tagName === 'TEXTAREA' && nativeTextAreaValueSetter) {
                                                    nativeTextAreaValueSetter.call(field, field.value);
                                                }
                                                
                                                // Trigger React's synthetic events with proper properties
                                                const inputEvent = new Event('input', { bubbles: true, cancelable: true });
                                                const changeEvent = new Event('change', { bubbles: true, cancelable: true });
                                                
                                                // Set target property for React
                                                Object.defineProperty(inputEvent, 'target', { value: field, enumerable: true });
                                                Object.defineProperty(changeEvent, 'target', { value: field, enumerable: true });
                                                
                                                // Also try React's specific event types
                                                field.dispatchEvent(inputEvent);
                                                field.dispatchEvent(changeEvent);
                                                
                                                // Try focus/blur to trigger React's onChange
                                                field.focus();
                                                field.dispatchEvent(new Event('focus', { bubbles: true }));
                                                field.dispatchEvent(new Event('blur', { bubbles: true }));
                                                
                                                // Try React's onChange directly if available
                                                if (field._valueTracker) {
                                                    field._valueTracker.setValue('');
                                                }
                                                field.value = field.value; // Re-set to trigger
                                                field.dispatchEvent(inputEvent);
                                            }
                                        }
                                    });
                                }
                            """)
                            await asyncio.sleep(2)  # Give more time for React to process
                            
                            # Verify field values are still set and re-fill if needed
                            field_values = await page.evaluate("""
                                () => {
                                    const form = document.querySelector('form');
                                    if (!form) return {};
                                    
                                    const values = {};
                                    const allFields = form.querySelectorAll('input, select, textarea');
                                    allFields.forEach(field => {
                                        if (field.type !== 'submit' && field.type !== 'button' && field.type !== 'hidden') {
                                            const name = field.name || field.id || 'unnamed';
                                            values[name] = field.value || '';
                                        }
                                    });
                                    return values;
                                }
                            """)
                            ultra_safe_log_print(f"   📋 Field values before submission: {field_values}")
                            
                            # Check if any required fields are empty and re-fill them
                            empty_fields = [name for name, value in field_values.items() if not value or value.strip() == '']
                            if empty_fields:
                                ultra_safe_log_print(f"   ⚠️  Some fields are empty: {empty_fields}, re-filling...")
                                # Re-fill empty fields using Playwright's fill() method
                                for field_name in empty_fields:
                                    try:
                                        # Try to find the field by name or id
                                        field = await page.query_selector(f'input[name="{field_name}"], textarea[name="{field_name}"], input[id="{field_name}"], textarea[id="{field_name}"]')
                                        if field:
                                            # Determine value based on field name
                                            value_to_fill = 'Test Value'
                                            field_name_lower = field_name.lower()
                                            if 'email' in field_name_lower:
                                                value_to_fill = 'test@example.com'
                                            elif 'name' in field_name_lower:
                                                value_to_fill = 'Test User'
                                            elif 'phone' in field_name_lower or 'telefoon' in field_name_lower:
                                                value_to_fill = '+1234567890'
                                            elif 'message' in field_name_lower or 'comment' in field_name_lower or 'bericht' in field_name_lower:
                                                value_to_fill = 'This is an automated test submission.'
                                            
                                            await field.fill(value_to_fill)
                                            await asyncio.sleep(0.3)
                                            ultra_safe_log_print(f"   ✅ Re-filled field: {field_name} = {value_to_fill}")
                                    except:
                                        pass
                                
                                # Verify again after re-filling
                                await asyncio.sleep(1)
                                field_values = await page.evaluate("""
                                    () => {
                                        const form = document.querySelector('form');
                                        if (!form) return {};
                                        
                                        const values = {};
                                        const allFields = form.querySelectorAll('input, select, textarea');
                                        allFields.forEach(field => {
                                            if (field.type !== 'submit' && field.type !== 'button' && field.type !== 'hidden') {
                                                const name = field.name || field.id || 'unnamed';
                                                values[name] = field.value || '';
                                            }
                                        });
                                        return values;
                                    }
                                """)
                                ultra_safe_log_print(f"   📋 Field values after re-fill: {field_values}")
                            
                            # Now try button click
                            ultra_safe_log_print("   📤 Trying button click first (may trigger JavaScript)...")
                            try:
                                # Click button to trigger any JavaScript handlers
                                await submit_btn.click(timeout=5000)
                                await asyncio.sleep(3)  # Wait for AJAX/JavaScript
                                ultra_safe_log_print("   ✅ Button clicked successfully")
                            except Exception as e:
                                ultra_safe_log_print(f"   ⚠️  Button click failed: {str(e)[:50]}, trying JavaScript click...")
                                try:
                                    # Fallback to JavaScript click
                                    await submit_btn.evaluate("(btn) => btn.click()")
                                    await asyncio.sleep(3)
                                    ultra_safe_log_print("   ✅ JavaScript click executed")
                                except:
                                    ultra_safe_log_print("   ⚠️  JavaScript click also failed, trying form.submit()...")
                                    # Last resort: form.submit()
                                    await page.evaluate("() => { const form = document.querySelector('form'); if (form) form.submit(); }")
                                    await asyncio.sleep(2)
                        except Exception as e:
                            ultra_safe_log_print(f"   ⚠️  form.submit() failed: {str(e)[:50]}")
                            # Try JavaScript click as fallback
                            try:
                                await submit_btn.evaluate("(btn) => btn.click()")
                                await asyncio.sleep(2)
                            except:
                                pass
                    else:
                        # For POST forms, try button click first
                        form_post_detected = False
                        try:
                            # Wait for response to form action URL
                            async def check_form_response(response):
                                nonlocal form_post_detected
                                if response.request.method == "POST":
                                    try:
                                        from urllib.parse import urlparse
                                        resp_domain = urlparse(response.url).netloc
                                        current_domain = urlparse(page.url).netloc if page.url else ""
                                        form_domain = urlparse(form_action_url).netloc if form_action_url else ""
                                        if (current_domain and resp_domain == current_domain) or (form_domain and resp_domain == form_domain):
                                            form_post_detected = True
                                            ultra_safe_log_print(f"   ✅ Form POST response received: {response.status} - {response.url[:100]}")
                                    except:
                                        pass
                            
                            page.on("response", check_form_response)
                            
                            # Try JavaScript click first (more reliable)
                            try:
                                # Clear AJAX submissions before clicking
                                await page.evaluate("() => { window.__ajaxSubmissions = []; window.__formSubmissionDetected = false; window.__formSubmissionSuccess = false; }")
                                
                                # Also set up response listener for POST requests
                                post_response_received = False
                                post_response_url = None
                                post_response_status = None
                                
                                async def check_post_response(response):
                                    nonlocal post_response_received, post_response_url, post_response_status
                                    if response.request.method == "POST":
                                        url = response.url
                                        # Check for contact form endpoints
                                        if any(keyword in url.lower() for keyword in ['contact', 'submit', 'form', 'message', 'api']):
                                            post_response_received = True
                                            post_response_url = url
                                            post_response_status = response.status
                                            ultra_safe_log_print(f"   ✅ POST response detected: {response.status} - {url[:100]}")
                                
                                page.on("response", check_post_response)
                                
                                # Check for error messages after click
                                await submit_btn.evaluate("(btn) => btn.click()")
                                ultra_safe_log_print("   ✅ Submit button clicked, waiting for AJAX submission...")
                                
                                # Wait longer for AJAX and check multiple times
                                for wait_attempt in range(8):
                                    await asyncio.sleep(2)
                                    
                                    # Check for AJAX submissions
                                    ajax_submissions = await page.evaluate("() => window.__ajaxSubmissions || []")
                                    if ajax_submissions:
                                        for submission in ajax_submissions:
                                            url = submission.get('url', '')
                                            method = submission.get('method', '').upper()
                                            # Check for contact form API endpoints
                                            if any(keyword in url.lower() for keyword in ['contact', 'submit', 'form', 'message', 'send']):
                                                ultra_safe_log_print(f"   ✅ Found contact form AJAX submission: {method} {url[:100]}")
                                                form_post_detected = True
                                                break
                                    
                                    # Check for error messages
                                    error_messages = await page.evaluate("""
                                        () => {
                                            const errors = [];
                                            const errorSelectors = [
                                                '.error', '.alert-error', '.alert-danger',
                                                '[role="alert"]', '.message-error',
                                                '.validation-error', '.form-error',
                                                '.text-red', '.text-danger'
                                            ];
                                            errorSelectors.forEach(selector => {
                                                const elements = document.querySelectorAll(selector);
                                                elements.forEach(el => {
                                                    if (el.textContent && el.offsetParent !== null) {
                                                        errors.push(el.textContent.trim());
                                                    }
                                                });
                                            });
                                            return errors;
                                        }
                                    """)
                                    if error_messages:
                                        ultra_safe_log_print(f"   ⚠️  Error messages on page: {error_messages[:3]}")
                                    
                                    # Check for success messages
                                    success_messages = await page.evaluate("""
                                        () => {
                                            const success = [];
                                            const successSelectors = [
                                                '.success', '.alert-success', '.message-success',
                                                '[role="alert"].success', '.text-green'
                                            ];
                                            successSelectors.forEach(selector => {
                                                const elements = document.querySelectorAll(selector);
                                                elements.forEach(el => {
                                                    if (el.textContent && el.offsetParent !== null) {
                                                        success.push(el.textContent.trim());
                                                    }
                                                });
                                            });
                                            return success;
                                        }
                                    """)
                                    if success_messages:
                                        ultra_safe_log_print(f"   ✅ Success messages: {success_messages[:2]}")
                                        form_post_detected = True
                                    
                                    if form_post_detected or post_response_received:
                                        if post_response_received:
                                            form_post_detected = True
                                            ultra_safe_log_print(f"   ✅ Form POST response confirmed: {post_response_status} - {post_response_url[:100]}")
                                        break
                                
                            except:
                                # Fallback to Playwright click with shorter timeout
                                await submit_btn.click(timeout=2000)
                                await asyncio.sleep(5)
                            
                            if not form_post_detected:
                                ultra_safe_log_print("   ⚠️  No form POST response detected, trying form.submit()...")
                                await page.evaluate("() => { const form = document.querySelector('form'); if (form) form.submit(); }")
                                await asyncio.sleep(2)
                        except Exception as e:
                            ultra_safe_log_print(f"   ⚠️  Error during submission: {str(e)[:50]}")
                            # Last resort: form.submit()
                            try:
                                await page.evaluate("() => { const form = document.querySelector('form'); if (form) form.submit(); }")
                                await asyncio.sleep(2)
                            except:
                                pass
                    
                    break
            except:
                continue
    except:
        pass
    
    # If button not found, try form.submit()
    if not submit_button_found:
        try:
            ultra_safe_log_print("   📤 Trying form.submit()...")
            post_requests.clear()
            post_responses.clear()
            form_submission_detected = False
            
            await page.evaluate("() => { const form = document.querySelector('form'); if (form) form.submit(); }")
            result["submission_attempted"] = True
            result["method_used"] = "form_submit"
        except:
            pass
    
    # Wait for POST requests/responses with longer timeout
    if result["submission_attempted"]:
        ultra_safe_log_print("   ⏳ Waiting for form submission...")
        
        # Check if form still exists (might indicate submission didn't work)
        try:
            form_still_exists = await page.evaluate("() => document.querySelector('form') !== null")
            if form_still_exists:
                ultra_safe_log_print("   ⚠️  Form still present on page - checking if submission occurred...")
        except:
            pass
        
        for wait_attempt in range(30):  # Wait up to 30 seconds (increased from 15)
            await asyncio.sleep(1)
            
            # Check for form POST/GET to the actual form URL
            try:
                form_submission_found = False
                # Check POST requests - VERIFY they contain form data
                for req in post_requests:
                    try:
                        from urllib.parse import urlparse
                        req_domain = urlparse(req['url']).netloc
                        current_domain = urlparse(page.url).netloc if page.url else ""
                        form_domain = urlparse(form_action_url).netloc if form_action_url else ""
                        if (current_domain and req_domain == current_domain) or (form_domain and req_domain == form_domain):
                            # Check if URL matches form action
                            if form_action_url and (req['url'] == form_action_url or req['url'].startswith(form_action_url.split('?')[0])):
                                # CRITICAL: Verify POST request contains form data
                                has_form_data = False
                                try:
                                    # Check if we captured form data for this request
                                    if form_submission_data and form_submission_data.get('url') == req['url']:
                                        has_form_data = True
                                        ultra_safe_log_print(f"   ✅ Form data verified in POST request")
                                    # Also check request post_data if available
                                    # Note: We can't access post_data from the request object here,
                                    # but we can check if form_submission_data was set
                                except:
                                    pass
                                
                                # Only mark as found if we have form data OR if URL clearly indicates form submission
                                url_lower = req['url'].lower()
                                is_form_endpoint = any(kw in url_lower for kw in ['contact', 'submit', 'form', 'message', 'send', 'mail', 'api/contact', 'api/submit'])
                                
                                if has_form_data or is_form_endpoint:
                                    form_submission_found = True
                                    form_submission_detected = True
                                    ultra_safe_log_print(f"   ✅ Found form POST to form URL: {req['url'][:100]}")
                                    if has_form_data:
                                        ultra_safe_log_print(f"      Form data confirmed in request")
                                    break
                                else:
                                    ultra_safe_log_print(f"   ⚠️  POST request found but no form data verified: {req['url'][:100]}")
                    except:
                        pass
                
                # Check GET requests (for GET contact forms)
                if not form_submission_found and contact_form_found:
                    for req in get_requests:
                        try:
                            from urllib.parse import urlparse
                            req_domain = urlparse(req['url']).netloc
                            current_domain = urlparse(page.url).netloc if page.url else ""
                            form_domain = urlparse(form_action_url).netloc if form_action_url else ""
                            if (current_domain and req_domain == current_domain) or (form_domain and req_domain == form_domain):
                                # Check if URL matches form action (with or without query params)
                                form_base = form_action_url.split('?')[0] if form_action_url else ""
                                req_base = req['url'].split('?')[0]
                                if form_base and (req_base == form_base or req['url'].startswith(form_base)):
                                    # Check if it has query parameters (form data was submitted)
                                    if '?' in req['url']:
                                        form_submission_found = True
                                        form_submission_detected = True
                                        ultra_safe_log_print(f"   ✅ Found form GET submission: {req['url'][:100]}")
                                        break
                        except:
                            pass
                
                if not form_submission_found and wait_attempt == 2:
                    # After 2 seconds, if no form submission found, try form.submit() again
                    ultra_safe_log_print("   🔄 No form submission detected, trying form.submit() again...")
                    try:
                        await page.evaluate("() => { const form = document.querySelector('form'); if (form) { form.submit(); } }")
                        await asyncio.sleep(1)
                    except:
                        pass
            except:
                pass
            
            if post_requests:
                result["post_requests"] = len(post_requests)
                for req in post_requests:
                    url_lower = req['url'].lower()
                    excluded = ['google-analytics', 'googletagmanager', 'google.com', 'pagead', 'clarity', 'facebook', 'twitter', 'doubleclick', 'getnitropack', 'analytics', 'gtm', 'ccm']
                    if not any(ex in url_lower for ex in excluded):
                        ultra_safe_log_print(f"   📤 Form POST request: {req['url'][:80]}")
                        # Check if this matches form action or domain
                        try:
                            from urllib.parse import urlparse
                            req_domain = urlparse(req['url']).netloc
                            form_domain = urlparse(form_action_url).netloc if form_action_url else ""
                            current_domain = urlparse(page.url).netloc if page.url else ""
                            if (form_domain and req_domain == form_domain) or (current_domain and req_domain == current_domain):
                                form_submission_detected = True
                                ultra_safe_log_print("   ✅ Form POST request matches domain!")
                        except:
                            pass
            
            if post_responses:
                result["post_responses"] = len(post_responses)
                for resp in post_responses:
                    url_lower = resp['url'].lower()
                    excluded = ['google-analytics', 'googletagmanager', 'google.com', 'pagead', 'clarity', 'facebook', 'twitter', 'doubleclick', 'getnitropack', 'analytics', 'gtm', 'ccm']
                    
                    # Skip analytics/tracking
                    if any(ex in url_lower for ex in excluded):
                        continue
                    
                    ultra_safe_log_print(f"   📥 Form POST response: {resp['status']} - {resp['url'][:80]}")
                    # Check if this is a form submission response by domain match
                    try:
                        from urllib.parse import urlparse
                        resp_domain = urlparse(resp['url']).netloc
                        form_domain = urlparse(form_action_url).netloc if form_action_url else ""
                        current_domain = urlparse(page.url).netloc if page.url else ""
                        
                        # STRICT: Must match form domain or current domain
                        if (form_domain and resp_domain == form_domain) or (current_domain and resp_domain == current_domain):
                            if resp['status'] in [200, 201, 204, 302, 303]:
                                form_submission_detected = True
                                ultra_safe_log_print(f"   ✅ Form submission confirmed: {resp['status']}")
                    except:
                        pass
            
            # Check for AJAX form submission
            try:
                ajax_submissions = await page.evaluate("() => window.__ajaxSubmissions || []")
                ajax_success = await page.evaluate("() => window.__formSubmissionSuccess || false")
                
                if ajax_submissions:
                    for submission in ajax_submissions:
                        url = submission.get('url', '')
                        method = submission.get('method', '').upper()
                        status = submission.get('response_status', 0)
                        response_data = submission.get('response_data', '')
                        body = submission.get('body') or submission.get('data', '')
                        
                        ultra_safe_log_print(f"   🔍 AJAX {submission.get('type', 'unknown')} {method}: {url[:100]}")
                        if body:
                            ultra_safe_log_print(f"      Request body: {str(body)[:200]}")
                        if status:
                            ultra_safe_log_print(f"      Response status: {status}")
                        if response_data:
                            ultra_safe_log_print(f"      Response data: {str(response_data)[:200]}")
                        
                        # Check if it's a contact form submission
                        url_lower = url.lower()
                        is_contact_endpoint = any(keyword in url_lower for keyword in [
                            'contact', 'submit', 'form', 'message', 'send', 'mail', 
                            'api/contact', 'api/submit', 'api/form', 'api/message'
                        ])
                        
                        # Check if it's to the form domain
                        try:
                            from urllib.parse import urlparse
                            ajax_domain = urlparse(url).netloc
                            current_domain = urlparse(page.url).netloc if page.url else ""
                            
                            if current_domain and ajax_domain == current_domain:
                                if is_contact_endpoint or status >= 200:
                                    form_submission_detected = True
                                    form_submission_response = {
                                        "url": url,
                                        "method": method,
                                        "status": status,
                                        "response_data": response_data[:500] if response_data else None
                                    }
                                    ultra_safe_log_print(f"   ✅ Contact form AJAX submission detected!")
                                    ultra_safe_log_print(f"      URL: {url[:100]}")
                                    ultra_safe_log_print(f"      Status: {status}")
                                    
                                    # CRITICAL: Check response status and body for errors
                                    submission_failed = False
                                    if status >= 400:
                                        submission_failed = True
                                        ultra_safe_log_print(f"      ❌ Submission failed with status {status}")
                                    
                                    # Check response body for error messages
                                    if response_data:
                                        response_lower = str(response_data).lower()
                                        # Check for common error indicators in JSON responses
                                        if '"success":false' in response_lower or '"error":' in response_lower:
                                            submission_failed = True
                                            ultra_safe_log_print(f"      ❌ Server returned error: {response_data[:200]}")
                                        # Check for error messages
                                        error_keywords = ['missing required', 'invalid', 'error', 'failed', 'required fields']
                                        if any(keyword in response_lower for keyword in error_keywords):
                                            submission_failed = True
                                            ultra_safe_log_print(f"      ❌ Error message in response: {response_data[:200]}")
                                    
                                    # Store submission failure status
                                    if submission_failed:
                                        form_submission_response["failed"] = True
                                        form_submission_response["error_reason"] = f"Status {status}" if status >= 400 else "Error in response"
                                    elif status >= 200 and status < 300:
                                        ultra_safe_log_print(f"      ✅ Submission successful!")
                        except:
                            pass
                
                # Also check the success flag
                if ajax_success:
                    ultra_safe_log_print(f"   ✅ AJAX submission success flag detected")
                    form_submission_detected = True
                    
                # Also check the old flag
                ajax_detected = await page.evaluate("() => window.__formSubmissionDetected || false")
                if ajax_detected:
                    ajax_url = await page.evaluate("() => window.__formSubmissionURL || ''")
                    ultra_safe_log_print(f"   ✅ AJAX form submission detected: {ajax_url[:80]}")
                    form_submission_detected = True
            except Exception as e:
                ultra_safe_log_print(f"   ⚠️  AJAX check error: {str(e)[:50]}")
                pass
            
            # Additional verification: Check if form fields are cleared (indicates submission)
            if wait_attempt >= 5:  # Only check after 5 seconds
                try:
                    form_fields_cleared = await page.evaluate("""
                        () => {
                            const form = document.querySelector('form');
                            if (!form) return { cleared: false, reason: 'no_form' };
                            
                            const inputs = Array.from(form.querySelectorAll('input:not([type="hidden"]):not([type="submit"]):not([type="button"]), textarea'));
                            let filled_count = 0;
                            let empty_count = 0;
                            
                            inputs.forEach(input => {
                                if (input.value && input.value.trim().length > 0) {
                                    filled_count++;
                                } else {
                                    empty_count++;
                                }
                            });
                            
                            // If most fields are empty, form was likely submitted
                            const cleared = empty_count > filled_count && inputs.length > 0;
                            return { cleared: cleared, filled: filled_count, empty: empty_count, total: inputs.length };
                        }
                    """)
                    
                    if form_fields_cleared.get('cleared') and not form_submission_detected:
                        ultra_safe_log_print(f"   🔍 Form fields appear cleared ({form_fields_cleared.get('empty')}/{form_fields_cleared.get('total')} empty) - possible submission")
                except:
                    pass
            
            if form_submission_detected:
                result["form_submission_detected"] = True
                # STRICT: Only mark as success if we have verified form data AND no errors
                
                # Check for submission failures (400, 500, error messages)
                submission_failed = False
                failure_reason = None
                
                # Check POST responses for error status codes
                for resp in post_responses:
                    if resp.get('status', 0) >= 400:
                        submission_failed = True
                        failure_reason = f"POST response status {resp.get('status')}"
                        ultra_safe_log_print(f"   ❌ Form submission failed: {failure_reason}")
                        break
                
                # Check AJAX submission responses
                try:
                    ajax_submissions = await page.evaluate("() => window.__ajaxSubmissions || []")
                    for submission in ajax_submissions:
                        status = submission.get('response_status', 0)
                        response_data = submission.get('response_data', '')
                        
                        if status >= 400:
                            submission_failed = True
                            failure_reason = f"AJAX response status {status}"
                            ultra_safe_log_print(f"   ❌ AJAX submission failed: {failure_reason}")
                            break
                        
                        # Check response body for error messages
                        if response_data:
                            response_str = str(response_data).lower()
                            if '"success":false' in response_str or '"error":' in response_str:
                                submission_failed = True
                                failure_reason = "Server returned error in response"
                                ultra_safe_log_print(f"   ❌ Server error in response: {response_data[:200]}")
                                break
                except:
                    pass
                
                # Check if form data contains actual values (not empty strings)
                if form_submission_data:
                    data_preview = form_submission_data.get('data_preview', '')
                    if data_preview:
                        # Check if all fields are empty in the submitted data
                        import json
                        try:
                            if isinstance(data_preview, str):
                                # Try to parse as JSON
                                if data_preview.startswith('{'):
                                    data_obj = json.loads(data_preview)
                                    # Check if all non-CAPTCHA fields are empty
                                    non_captcha_fields = {k: v for k, v in data_obj.items() if 'captcha' not in k.lower() and 'token' not in k.lower()}
                                    if non_captcha_fields and all(not str(v).strip() for v in non_captcha_fields.values()):
                                        submission_failed = True
                                        failure_reason = "All form fields are empty in submission data"
                                        ultra_safe_log_print(f"   ❌ Form submission failed: {failure_reason}")
                        except:
                            # If not JSON, check if it's a query string with empty values
                            if '=' in data_preview:
                                params = data_preview.split('&')
                                non_captcha_params = [p for p in params if 'captcha' not in p.lower() and 'token' not in p.lower()]
                                if non_captcha_params and all('=' in p and (p.split('=')[1] == '' or p.split('=')[1] == 'null') for p in non_captcha_params):
                                    submission_failed = True
                                    failure_reason = "All form fields are empty in submission data"
                                    ultra_safe_log_print(f"   ❌ Form submission failed: {failure_reason}")
                
                if form_submission_data and not submission_failed:
                    result["submission_success"] = True
                    ultra_safe_log_print("   ✅ Form submission confirmed with verified form data!")
                    break
                elif submission_failed:
                    result["submission_success"] = False
                    ultra_safe_log_print(f"   ❌ Form submission failed: {failure_reason}")
                    break
                elif wait_attempt >= 20:  # Wait at least 20 seconds before accepting without form data
                    # Even after 20 seconds, only mark as success if we have strong indicators
                    # Check for success messages on page
                    try:
                        page_content = await page.content()
                        content_lower = page_content.lower()
                        strong_indicators = ['thank you', 'success', 'received', 'submitted successfully', 'message sent']
                        has_strong_indicator = any(indicator in content_lower for indicator in strong_indicators)
                        if has_strong_indicator:
                            result["submission_success"] = True
                            ultra_safe_log_print("   ✅ Form submission confirmed by success message on page!")
                            break
                        else:
                            ultra_safe_log_print("   ⚠️  Form submission detected but no form data or success message - marking as attempted only")
                            result["submission_success"] = False
                            break
                    except:
                        ultra_safe_log_print("   ⚠️  Form submission detected but no form data - marking as attempted only")
                        result["submission_success"] = False
                        break
                else:
                    ultra_safe_log_print("   ⏳ Form submission detected but waiting for form data verification...")
                    # Continue waiting to verify
            
            # Check for success indicators on page (but require form_submission_data for strict verification)
            try:
                page_content = await page.content()
                content_lower = page_content.lower()
                success_indicators = ['thank you', 'thankyou', 'success', 'received', 'submitted successfully', 'message sent', 'your message has been']
                if any(indicator in content_lower for indicator in success_indicators):
                    # Only mark as success if we also have form data OR if we've waited long enough
                    if form_submission_data or wait_attempt >= 15:
                        result["submission_success"] = True
                        ultra_safe_log_print("   ✅ Success indicators found on page!")
                        # If success indicators found, also mark as detected
                        if not form_submission_detected:
                            form_submission_detected = True
                            result["form_submission_detected"] = True
                        break
                    else:
                        ultra_safe_log_print("   ⏳ Success message found but waiting for form data verification...")
            except:
                pass
    
    # Final check: if we have POST requests to the form URL, consider it submitted
    # BUT: Only if we have form_submission_data to verify actual form submission
    if not form_submission_detected and post_requests:
        for req in post_requests:
            url_lower = req['url'].lower()
            excluded = ['google-analytics', 'googletagmanager', 'clarity', 'facebook', 'twitter', 'doubleclick', 'getnitropack']
            # Also exclude CSS/JS files and other resources
            excluded_extensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.ico', '.map']
            excluded_paths = ['wp-includes', 'wp-content', '/static/', '/assets/', '/css/', '/js/', '/wp-json/', '/api/', '/dist/', '/build/']
            is_excluded_resource = any(ext in url_lower for ext in excluded_extensions) or any(path in url_lower for path in excluded_paths)
            if not any(ex in url_lower for ex in excluded) and not is_excluded_resource:
                # Check if URL matches form domain
                try:
                    from urllib.parse import urlparse
                    req_domain = urlparse(req['url']).netloc
                    current_domain = urlparse(page.url).netloc if page.url else ""
                    form_domain = urlparse(form_action_url).netloc if form_action_url else ""
                    
                    # STRICT: Only mark as submitted if:
                    # 1. URL matches form action OR
                    # 2. URL contains form keywords AND we have form_submission_data
                    url_matches_action = False
                    if form_action_url:
                        form_base = form_action_url.split('?')[0]
                        req_base = req['url'].split('?')[0]
                        url_matches_action = req_base == form_base or req['url'].startswith(form_base)
                    
                    is_form_endpoint = any(kw in url_lower for kw in ['contact', 'submit', 'send', 'message', 'form', 'api/contact', 'api/submit'])
                    has_form_data = form_submission_data and (form_submission_data.get('url') == req['url'] or form_submission_data.get('url', '').startswith(req['url'].split('?')[0]))
                    
                    # Match by domain AND (form action OR form endpoint with data)
                    if current_domain and req_domain == current_domain:
                        if url_matches_action or (is_form_endpoint and has_form_data):
                            form_submission_detected = True
                            ultra_safe_log_print(f"   ✅ Form submission detected by domain match: {req['url'][:80]}")
                            if has_form_data:
                                ultra_safe_log_print(f"      Form data verified in request")
                            break
                    # Match by form action
                    if form_domain and req_domain == form_domain:
                        if url_matches_action or (is_form_endpoint and has_form_data):
                            form_submission_detected = True
                            ultra_safe_log_print(f"   ✅ Form submission detected by form action match: {req['url'][:80]}")
                            if has_form_data:
                                ultra_safe_log_print(f"      Form data verified in request")
                            break
                except:
                    pass
        
        # Also check responses
        if not form_submission_detected and post_responses:
            for resp in post_responses:
                url_lower = resp['url'].lower()
                excluded = ['google-analytics', 'googletagmanager', 'clarity', 'facebook', 'twitter', 'doubleclick', 'getnitropack']
                if not any(ex in url_lower for ex in excluded):
                    try:
                        from urllib.parse import urlparse
                        resp_domain = urlparse(resp['url']).netloc
                        current_domain = urlparse(page.url).netloc if page.url else ""
                        if current_domain and resp_domain == current_domain and resp['status'] in [200, 201, 204, 302, 303, 419]:
                            form_submission_detected = True
                            ultra_safe_log_print(f"   ✅ Form submission detected by response: {resp['status']} - {resp['url'][:80]}")
                            break
                    except:
                        pass
    
    # Update final counts
    result["post_requests"] = len(post_requests)
    result["post_responses"] = len(post_responses)
    result["get_requests"] = len(get_requests)
    result["form_submission_detected"] = form_submission_detected
    if form_submission_data:
        result["form_submission_data"] = form_submission_data
    
    # Check GET requests for GET form submissions
    if not form_submission_detected and get_requests and contact_form_found:
        for req in get_requests:
            try:
                from urllib.parse import urlparse
                req_domain = urlparse(req['url']).netloc
                current_domain = urlparse(page.url).netloc if page.url else ""
                form_domain = urlparse(form_action_url).netloc if form_action_url else ""
                if (current_domain and req_domain == current_domain) or (form_domain and req_domain == form_domain):
                    form_base = form_action_url.split('?')[0] if form_action_url else ""
                    req_base = req['url'].split('?')[0]
                    if form_base and (req_base == form_base or req['url'].startswith(form_base)):
                        if '?' in req['url']:  # Has query params = form data submitted
                            # Verify query params contain form fields
                            try:
                                from urllib.parse import urlparse, parse_qs
                                query_string = urlparse(req['url']).query
                                query_params = parse_qs(query_string)
                                # Check if query params contain form fields
                                has_form_fields = any(key.lower() in ['name', 'email', 'message', 'phone', 'subject', 'contact'] for key in query_params.keys())
                                if has_form_fields:
                                    form_submission_detected = True
                                    result["form_submission_detected"] = True
                                    result["submission_success"] = True
                                    ultra_safe_log_print("   ✅ Form submission detected (GET with form data in query params)")
                                    break
                                else:
                                    ultra_safe_log_print(f"   ⚠️  GET request has query params but no form fields: {req['url'][:80]}")
                            except:
                                # If we can't parse, be conservative
                                ultra_safe_log_print(f"   ⚠️  GET request with query params but couldn't verify form data: {req['url'][:80]}")
                                pass
            except:
                pass
    
    # STRICT: Only mark as detected if we have verified form data
    # Don't mark as success just because there's a POST request - require form data verification
    if result["post_requests"] > 0 and not form_submission_detected:
        # Check if any POST request is to the same domain AND has form data
        for req in post_requests:
            try:
                from urllib.parse import urlparse
                req_domain = urlparse(req['url']).netloc
                current_domain = urlparse(page.url).netloc if page.url else ""
                if current_domain and req_domain == current_domain:
                    # CRITICAL: Only mark as detected if we have form_submission_data
                    if form_submission_data:
                        form_submission_detected = True
                        result["form_submission_detected"] = True
                        ultra_safe_log_print("   ✅ Form submission verified (POST with form data)")
                        break
                    else:
                        # Check if URL suggests it's a form endpoint
                        url_lower = req['url'].lower()
                        is_form_endpoint = any(kw in url_lower for kw in ['contact', 'submit', 'send', 'message', 'form', 'api/contact', 'api/submit', 'api/message'])
                        if is_form_endpoint:
                            ultra_safe_log_print(f"   ⚠️  POST to form endpoint but no form data captured: {req['url'][:80]}")
                            ultra_safe_log_print("   ⚠️  Submission NOT verified - may be a false positive")
            except:
                pass
    
    return result

async def run_ultra_resilient_submission(url: str, template_path: Path) -> Dict[str, Any]:
    """ULTRA-RESILIENT main submission function - CANNOT FAIL."""
    
    # Get heartbeat file path for debugging
    heartbeat_file_path = None
    try:
        heartbeat_file_path = Path('/var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_script_heartbeat_' + str(os.getpid()) + '.txt')
        if not heartbeat_file_path.exists():
            heartbeat_file_path = Path('/tmp/python_script_heartbeat_' + str(os.getpid()) + '.txt')
    except:
        pass
    
    # Update heartbeat - function entry
    try:
        if heartbeat_file_path and heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write("📍 [run_ultra_resilient_submission] Function entry\n")
                f.write(f"📍 [run_ultra_resilient_submission] URL: {url}\n")
                f.write(f"📍 [run_ultra_resilient_submission] Template: {template_path}\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    # Initialize result with multiple fallback values
    result = {
        "status": "unknown",
        "message": "Process initialized",
        "url": url,
        "error_type": None,
        "recovered": False,
        "steps_completed": [],
        "timestamp": time.time(),
        "attempt_id": int(time.time() * 1000)
    }
    
    # Step 1: Load template (cannot fail) - need to load before creating manager
    try:
        if heartbeat_file_path and heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write("📍 [run_ultra_resilient_submission] About to load template\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    ultra_safe_log_print("=" * 80)
    ultra_safe_log_print("🚀 STARTING AUTOMATION")
    ultra_safe_log_print("=" * 80)
    ultra_safe_log_print(f"📋 Loading template from: {template_path}")
    template = await ultra_safe_template_load(template_path)
    
    try:
        if heartbeat_file_path and heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write("📍 [run_ultra_resilient_submission] Template loaded\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    result["steps_completed"].append("template_loaded")
    result["template_used"] = "custom" if template.get("fields") else "default"
    ultra_safe_log_print(f"✅ Template loaded: {result['template_used']} template")
    
    # Get headless setting from template (default to False for better CAPTCHA solving)
    headless_mode = template.get("headless", False)
    if headless_mode:
        ultra_safe_log_print("🖥️  Running in headless mode")
    else:
        ultra_safe_log_print("🖥️  Running in visible browser mode (better for CAPTCHA solving)")
    
    try:
        if heartbeat_file_path and heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write("📍 [run_ultra_resilient_submission] About to create PlaywrightManager\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    ultra_safe_log_print(f"🔧 Creating PlaywrightManager instance...")
    playwright_manager = UltimatePlaywrightManager(headless=headless_mode)
    ultra_safe_log_print(f"✅ PlaywrightManager created")
    
    try:
        if heartbeat_file_path and heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write("📍 [run_ultra_resilient_submission] PlaywrightManager created\n")
                f.write("📍 [run_ultra_resilient_submission] About to call playwright_manager.start()\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    try:
        # Step 2: Initialize Playwright (cannot fail)
        ultra_safe_log_print(f"🚀 Initializing browser (headless={headless_mode})...")
        ultra_safe_log_print(f"   📍 About to call playwright_manager.start()...")
        sys.stderr.flush()
        
        playwright_ready = await playwright_manager.start()
        
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [run_ultra_resilient_submission] playwright_manager.start() returned: {playwright_ready}\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        ultra_safe_log_print(f"   📍 playwright_manager.start() returned: {playwright_ready}")
        sys.stderr.flush()
        
        if not playwright_ready:
            # Get detailed error information
            current_display = os.environ.get('DISPLAY', 'NOT SET')
            xvfb_available = subprocess.run(['which', 'Xvfb'], capture_output=True).returncode == 0
            error_details = []
            error_details.append("❌ Browser initialization failed")
            error_details.append("")
            error_details.append("Diagnostic Information:")
            error_details.append(f"  DISPLAY: {current_display}")
            error_details.append(f"  Xvfb available: {'Yes' if xvfb_available else 'No'}")
            error_details.append("")
            error_details.append("Common causes:")
            error_details.append("  1. Missing DISPLAY environment variable")
            error_details.append("  2. Xvfb not installed or not working")
            error_details.append("  3. Browser binaries not installed")
            error_details.append("  4. System dependencies missing")
            error_details.append("")
            error_details.append("Check the logs above for specific error messages.")
            
            error_msg = "\n".join(error_details)
            ultra_safe_log_print(f"❌ {error_msg}")
            result.update({
                "status": "error",
                "message": error_msg,
                "error_type": "browser_init_failed",
                "recovered": True
            })
            return result
        
        ultra_safe_log_print("✅ Browser initialized successfully")
        result["steps_completed"].append("browser_ready")
        
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [run_ultra_resilient_submission] Browser initialized successfully\n")
                    f.write("📍 [run_ultra_resilient_submission] About to navigate to URL\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        # Step 3: Navigate to URL (cannot fail)
        ultra_safe_log_print(f"🌐 Navigating to URL: {url}")
        # Track form load timestamp for WPForms
        form_load_timestamp = time.time()
        navigation_success = await playwright_manager.navigate(url)
        
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [run_ultra_resilient_submission] Navigation result: {navigation_success}\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        if not navigation_success:
            error_msg = f"Navigation failed to {url}"
            ultra_safe_log_print(f"❌ {error_msg}")
            result.update({
                "status": "error", 
                "message": error_msg + "\n\nThis usually means the page failed to load or timed out.",
                "error_type": "navigation_failed",
                "recovered": True
            })
            return result
        
        result["steps_completed"].append("navigation_complete")
        result["final_url"] = await UltimateSafetyWrapper.execute_async(
            lambda: playwright_manager.page.url,
            default_return=url
        )
        
        # Extract WPForms fields right after navigation (to get form load timestamp)
        wpforms_data = {}
        try:
            wpforms_data = await extract_wpforms_fields(playwright_manager.page, form_load_timestamp)
            if wpforms_data.get('is_wpforms'):
                ultra_safe_log_print("🔑 WPForms detected - extracted form fields")
                if wpforms_data.get('token'):
                    ultra_safe_log_print(f"   🔑 Token: {wpforms_data['token'][:20]}...")
                if wpforms_data.get('form_id'):
                    ultra_safe_log_print(f"   📋 Form ID: {wpforms_data['form_id']}")
                if wpforms_data.get('start_timestamp'):
                    ultra_safe_log_print(f"   ⏰ Start timestamp: {wpforms_data['start_timestamp']}")
                result["wpforms_data"] = wpforms_data
        except Exception as e:
            ultra_safe_log_print(f"   ⚠️  Could not extract WPForms fields: {str(e)[:50]}")
        
        # Step 3.5: Handle banners, popups, and cookie consent (CRITICAL - must be done before form interaction)
        ultra_safe_log_print("")
        ultra_safe_log_print("🚫 STEP 3.5: Handling banners, popups, and cookie consent...")
        ultra_safe_log_print("-" * 80)
        banners_closed = await handle_banners_and_popups(playwright_manager.page)
        result["banners_closed"] = banners_closed
        if banners_closed > 0:
            ultra_safe_log_print(f"✅ Closed {banners_closed} banner(s)/popup(s)")
        else:
            ultra_safe_log_print("ℹ️  No banners or popups detected")
        ultra_safe_log_print("")
        
        # Step 3.6: Ensure forms appear above all banners with high z-index
        ultra_safe_log_print("📋 STEP 3.6: Ensuring forms appear above banners...")
        ultra_safe_log_print("-" * 80)
        forms_updated = await playwright_manager.page.evaluate("""
            () => {
                const forms = document.querySelectorAll('form');
                let updated = 0;
                
                forms.forEach(form => {
                    // Apply high z-index and position relative to ensure form is above banners
                    form.style.position = 'relative';
                    form.style.zIndex = '999999';
                    form.style.backgroundColor = form.style.backgroundColor || 'transparent';
                    updated++;
                });
                
                return updated;
            }
        """)
        
        if forms_updated > 0:
            ultra_safe_log_print(f"✅ Applied high z-index to {forms_updated} form(s) to ensure they appear above banners")
        else:
            ultra_safe_log_print("ℹ️  No forms found to update")
        ultra_safe_log_print("")
        
        # Check if there's a contact form, if not try to find contact page
        try:
            has_contact_form = await playwright_manager.page.evaluate("""
                () => {
                    const forms = document.querySelectorAll('form');
                    for (const form of forms) {
                        const method = (form.method || 'get').toLowerCase();
                        const formText = form.textContent.toLowerCase();
                        const formId = (form.id || '').toLowerCase();
                        const formClass = (form.className || '').toLowerCase();
                        
                        // Check if it's a search form (skip)
                        const isSearch = method === 'get' && (
                            formText.includes('search') ||
                            formId.includes('search') ||
                            formClass.includes('search')
                        );
                        
                        // Check if it's a contact form
                        // Contact form should have: name, email, and comment/message fields
                        const hasNameField = form.querySelector('input[name="name"]');
                        const hasEmailField = form.querySelector('input[name="email"]');
                        const hasPhoneField = form.querySelector('input[name="phone"]');
                        const hasCommentField = form.querySelector('textarea[name="comment"]') || form.querySelector('textarea[name="message"]');
                        
                        // Contact form must have at least name, email, and comment
                        const isContact = (hasNameField && hasEmailField && hasCommentField) || 
                                        method === 'post' || (
                            formText.includes('contact') ||
                            formId.includes('contact') ||
                            formClass.includes('contact') ||
                            (hasNameField && hasEmailField)  // At least name and email
                        );
                        
                        if (isContact && !isSearch) {
                            return true;
                        }
                    }
                    return false;
                }
            """)
            
            # Always check for contactInfo section first (even if has_contact_form is false)
            # Scroll down to load content if needed
            await playwright_manager.page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            await asyncio.sleep(1)
            
            contact_form_result = await playwright_manager.page.evaluate("""
                () => {
                    // Try multiple selectors for contact section
                    const contactSection = document.querySelector('.contactInfo, section.contactInfo, [class*="contactInfo"]');
                    
                    // Also try to find form with contact fields anywhere on page
                    const allForms = document.querySelectorAll('form');
                    let contactForm = null;
                    
                    for (const form of allForms) {
                        const hasName = form.querySelector('input[name="name"]');
                        const hasEmail = form.querySelector('input[name="email"]');
                        const hasComment = form.querySelector('textarea[name="comment"]') || form.querySelector('textarea[name="message"]');
                        
                        if (hasName && hasEmail && hasComment) {
                            contactForm = form;
                            break;
                        }
                    }
                    
                    if (contactForm) {
                        // Scroll to the form
                        if (contactSection) {
                            contactSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        } else {
                            contactForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                        return true;
                    }
                    
                    return false;
                }
            """)
            
            if contact_form_result:
                ultra_safe_log_print("✅ Found contact form with name, email, comment fields - scrolled to it")
                await asyncio.sleep(2)  # Wait for scroll and content to load
                # Don't navigate away if we found the contact form
                has_contact_form = True
                
            if not has_contact_form and not contact_form_result:
                    ultra_safe_log_print("🔍 No contact form found, looking for contact page...")
                    contact_link = await playwright_manager.page.evaluate("""
                        () => {
                            // Look for contact links
                            const links = Array.from(document.querySelectorAll('a[href*="contact"]'));
                            if (links.length > 0) {
                                return links[0].href;
                            }
                            // Try common contact page paths
                            const currentUrl = window.location.href;
                            const baseUrl = currentUrl.replace(/\\/$/, '');
                            const commonPaths = ['/contact', '/contact-us', '/contactus', '/get-in-touch'];
                            for (const path of commonPaths) {
                                return baseUrl + path;
                            }
                            return null;
                        }
                    """)
                    
                    if contact_link:
                        ultra_safe_log_print(f"🔗 Found contact page: {contact_link[:80]}")
                        ultra_safe_log_print("🌐 Navigating to contact page...")
                        nav_success = await playwright_manager.navigate(contact_link)
                        if nav_success:
                            result["final_url"] = contact_link
                            ultra_safe_log_print("✅ Navigated to contact page")
                            # Wait a bit for dynamic content to load
                            await asyncio.sleep(2)
                        else:
                            ultra_safe_log_print("⚠️  Failed to navigate to contact page")
                    else:
                        ultra_safe_log_print("⚠️  No contact page found - please provide contact page URL")
        except:
            pass  # Continue anyway
        
        # Step 4: Handle CAPTCHAs with LOCAL solver (cannot fail)
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [run_ultra_resilient_submission] Step 4: About to handle CAPTCHAs\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        ultra_safe_log_print("🔐 Checking for CAPTCHAs (using LOCAL solver)...")
        
        # First, do a quick check to see if CAPTCHA is actually present
        quick_captcha_check = await playwright_manager.page.evaluate("""
            () => {
                // Quick strict check for actual CAPTCHA widgets
                const hasRecaptcha = document.querySelector('.g-recaptcha[data-sitekey]') || 
                                     document.querySelector('textarea[name="g-recaptcha-response"]');
                const hasHcaptcha = document.querySelector('.h-captcha[data-sitekey]') || 
                                    document.querySelector('textarea[name="h-captcha-response"]');
                const hasHashcash = document.querySelector('button[data-rsfp-hashcash], button[data-hashcash-level]');
                
                return {
                    has_captcha: !!(hasRecaptcha || hasHcaptcha || hasHashcash),
                    has_recaptcha: !!hasRecaptcha,
                    has_hcaptcha: !!hasHcaptcha,
                    has_hashcash: !!hasHashcash
                };
            }
        """)
        
        if not quick_captcha_check.get('has_captcha'):
            ultra_safe_log_print("ℹ️  No CAPTCHA detected on page - skipping CAPTCHA handling")
            captcha_result = {
                "captchas_detected": 0,
                "captchas_solved": 0,
                "solutions": []
            }
            result["captcha_result"] = captcha_result
            result["steps_completed"].append("captcha_handled")
        else:
            # CAPTCHA detected, proceed with handling
            ultra_safe_log_print(f"🔐 CAPTCHA detected: reCAPTCHA={quick_captcha_check.get('has_recaptcha')}, hCaptcha={quick_captcha_check.get('has_hcaptcha')}, Hashcash={quick_captcha_check.get('has_hashcash')}")
        
        # Check for rate limit error in reCAPTCHA challenge iframe BEFORE attempting to solve
        try:
            rate_limit_in_iframe = await playwright_manager.page.evaluate("""
                () => {
                    // Check for the specific HTML structure in challenge iframe
                    // Look for: <div class="rc-doscaptcha-header-text">Try again later</div>
                    const challengeIframes = document.querySelectorAll('iframe[title*="challenge"], iframe[src*="bframe"], iframe[src*="recaptcha/api2/bframe"]');
                    for (const iframe of challengeIframes) {
                        try {
                            const iframeDoc = iframe.contentDocument || iframe.contentWindow?.document;
                            if (iframeDoc) {
                                // Check for the specific class structure
                                const headerText = iframeDoc.querySelector('.rc-doscaptcha-header-text');
                                if (headerText) {
                                    const headerTextContent = headerText.textContent || headerText.innerText || '';
                                    if (headerTextContent.toLowerCase().includes('try again later')) {
                                        return true;
                                    }
                                }
                                
                                // Also check body text
                                const bodyText = iframeDoc.querySelector('.rc-doscaptcha-body-text');
                                if (bodyText) {
                                    const bodyTextContent = bodyText.textContent || bodyText.innerText || '';
                                    const bodyTextLower = bodyTextContent.toLowerCase();
                                    if (bodyTextLower.includes('automated queries') || 
                                        bodyTextLower.includes('can\'t process your request')) {
                                        return true;
                                    }
                                }
                            }
                        } catch (e) {
                            // Cross-origin, try alternative
                        }
                    }
                    
                    // Also check page text
                    const pageText = document.body.innerText || document.body.textContent || '';
                    const errorMessages = [
                        'Try again later',
                        'automated queries',
                        'can\'t process your request',
                        'Your computer or network may be sending automated queries'
                    ];
                    const textLower = pageText.toLowerCase();
                    return errorMessages.some(msg => textLower.includes(msg.toLowerCase()));
                }
            """)
            if rate_limit_in_iframe:
                ultra_safe_log_print("   ⚠️  reCAPTCHA rate limit error detected in challenge iframe")
                ultra_safe_log_print("   🔄 Closing browser and restarting ENTIRE process from beginning...")
                
                # Close current browser session
                try:
                    await playwright_manager.cleanup()
                    ultra_safe_log_print("   ✅ Browser closed")
                except:
                    pass
                
                # Wait before restarting
                wait_time = 10
                ultra_safe_log_print(f"   ⏳ Waiting {wait_time} seconds before restarting browser...")
                await asyncio.sleep(wait_time)
                
                # Restart browser
                ultra_safe_log_print("   🔄 Restarting browser...")
                playwright_ready = await playwright_manager.start()
                if playwright_ready:
                    ultra_safe_log_print(f"   🌐 Navigating back to URL: {url}")
                    nav_success = await playwright_manager.navigate(url)
                    if nav_success:
                        await asyncio.sleep(3)
                        await handle_banners_and_popups(playwright_manager.page)
                        ultra_safe_log_print("   ✅ Browser restarted, will restart from form finding...")
                        # Return a special flag to restart the entire process
                        raise Exception("RECAPTCHA_RATE_LIMIT_RESTART_FULL")
        except Exception as e:
            if "RECAPTCHA_RATE_LIMIT_RESTART_FULL" in str(e):
                raise  # Re-raise to trigger full restart
            pass  # Continue if check fails
        
        # Try to handle CAPTCHAs with retry on rate limit (only if CAPTCHA was detected)
        if quick_captcha_check.get('has_captcha'):
            max_captcha_retries = 2
            captcha_result = None
            for captcha_retry in range(max_captcha_retries):
                try:
                    captcha_result = await playwright_manager.handle_captchas()
                    result["captcha_result"] = captcha_result
                    result["steps_completed"].append("captcha_handled")
                    break  # Success, exit retry loop
                except Exception as e:
                    error_msg = str(e)
                    if "RECAPTCHA_RATE_LIMIT" in error_msg or "rate limit" in error_msg.lower():
                        ultra_safe_log_print(f"   ⚠️  reCAPTCHA rate limit detected (attempt {captcha_retry + 1}/{max_captcha_retries})")
                        ultra_safe_log_print("   🔄 Closing browser and restarting to bypass rate limit...")
                        
                        # Close current browser session
                        try:
                            await playwright_manager.cleanup()
                            ultra_safe_log_print("   ✅ Browser closed")
                        except:
                            pass
                        
                        # Wait before restarting (give Google time to reset)
                        wait_time = 10 + (captcha_retry * 5)  # 10s, 15s, etc.
                        ultra_safe_log_print(f"   ⏳ Waiting {wait_time} seconds before restarting browser...")
                        await asyncio.sleep(wait_time)
                        
                        # Restart browser
                        ultra_safe_log_print("   🔄 Restarting browser...")
                        playwright_ready = await playwright_manager.start()
                        if not playwright_ready:
                            ultra_safe_log_print("   ❌ Failed to restart browser")
                            break
                        
                        # Navigate back to the URL
                        ultra_safe_log_print(f"   🌐 Navigating back to URL: {url}")
                        nav_success = await playwright_manager.navigate(url)
                        if not nav_success:
                            ultra_safe_log_print("   ❌ Failed to navigate back to URL")
                            break
                        
                        # Wait for page to load
                        await asyncio.sleep(3)
                        
                        # Handle banners again after restart
                        await handle_banners_and_popups(playwright_manager.page)
                        
                        ultra_safe_log_print("   ✅ Browser restarted, retrying CAPTCHA solving...")
                        continue  # Retry CAPTCHA solving
                    elif "RECAPTCHA_RATE_LIMIT_RESTART_FULL" in error_msg:
                        # Full restart required - re-raise to trigger restart from beginning
                        ultra_safe_log_print("   ⚠️  Full restart required due to rate limit")
                        raise  # Re-raise to trigger full restart
                    else:
                        # Other error, just log and break
                        ultra_safe_log_print(f"   ⚠️  CAPTCHA handling error: {error_msg[:100]}")
                        break
        
            if captcha_result is None:
                # Create empty result if all retries failed
                captcha_result = {
                    "captchas_detected": 0,
                    "captchas_solved": 0,
                    "solutions": []
                }
                result["captcha_result"] = captcha_result
        
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [run_ultra_resilient_submission] Step 4: CAPTCHA handled, detected: {captcha_result.get('captchas_detected', 0)}\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        # Step 5: Simple form filling (cannot fail)
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [run_ultra_resilient_submission] Step 5: About to fill form fields\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        ultra_safe_log_print("")
        ultra_safe_log_print("✍️  STEP 5: Filling form fields...")
        ultra_safe_log_print("-" * 80)
        fill_result = await ultra_simple_form_fill(playwright_manager.page, template)
        result.update(fill_result)
        result["steps_completed"].append("form_filled")
        ultra_safe_log_print(f"✅ Form filling completed: {fill_result.get('fields_filled', 0)} field(s) filled")
        ultra_safe_log_print("")
        
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [run_ultra_resilient_submission] Step 5: Form filled, fields: {fill_result.get('fields_filled', 0)}\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        # Step 5.5: Check and solve CAPTCHA again (after form filling, CAPTCHA might be visible now)
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [run_ultra_resilient_submission] Step 5.5: Re-checking CAPTCHAs after form fill\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        ultra_safe_log_print("🔐 STEP 5.5: Re-checking CAPTCHAs after form fill...")
        ultra_safe_log_print("-" * 80)
        captcha_result_after = None
        
        # Quick check: Skip CAPTCHA re-check if page is already closed
        page_valid_for_captcha = True
        try:
            if not playwright_manager.page:
                page_valid_for_captcha = False
                ultra_safe_log_print("⚠️  Page is None, skipping CAPTCHA re-check")
            elif playwright_manager.page.is_closed():
                page_valid_for_captcha = False
                ultra_safe_log_print("⚠️  Page is closed, skipping CAPTCHA re-check")
        except Exception as e:
            page_valid_for_captcha = False
            ultra_safe_log_print(f"⚠️  Cannot verify page status: {str(e)[:50]}")
        
        if not page_valid_for_captcha:
            captcha_result_after = {
                "captchas_detected": 0,
                "captchas_solved": 0,
                "solutions": []
            }
            ultra_safe_log_print("ℹ️  Skipping CAPTCHA re-check, proceeding to form submission")
        else:
            # Set a timeout for CAPTCHA re-check to prevent hanging
            try:
                captcha_result_after = await asyncio.wait_for(
                    playwright_manager.handle_captchas(),
                    timeout=30.0  # Max 30 seconds for CAPTCHA re-check
                )
            except asyncio.TimeoutError:
                ultra_safe_log_print("⚠️  CAPTCHA re-check timed out (30s), proceeding to form submission")
                captcha_result_after = {
                    "captchas_detected": 0,
                    "captchas_solved": 0,
                    "solutions": []
                }
            except Exception as e:
                error_msg = str(e)
                ultra_safe_log_print(f"⚠️  CAPTCHA re-check error: {error_msg[:50]}")
                # Check if page closed during CAPTCHA handling
                try:
                    if playwright_manager.page and playwright_manager.page.is_closed():
                        ultra_safe_log_print("⚠️  Page closed during CAPTCHA re-check")
                    else:
                        ultra_safe_log_print("ℹ️  CAPTCHA re-check failed but page is still open, proceeding to submission")
                except:
                    pass
                captcha_result_after = {
                    "captchas_detected": 0,
                    "captchas_solved": 0,
                    "solutions": []
                }
        
        if captcha_result_after and captcha_result_after.get("captchas_solved", 0) > 0:
            ultra_safe_log_print(f"✅ CAPTCHA solved after form fill: {captcha_result_after.get('captchas_solved')} solved")
            # Aggregate CAPTCHA counts instead of replacing
            if "captcha_result" in result:
                result["captcha_result"]["captchas_solved"] = result["captcha_result"].get("captchas_solved", 0) + captcha_result_after.get("captchas_solved", 0)
                result["captcha_result"]["captchas_detected"] = max(
                    result["captcha_result"].get("captchas_detected", 0),
                    captcha_result_after.get("captchas_detected", 0)
                )
                if captcha_result_after.get("solutions"):
                    result["captcha_result"]["solutions"].extend(captcha_result_after.get("solutions", []))
            else:
                result["captcha_result"] = captcha_result_after
        else:
            ultra_safe_log_print("ℹ️  No additional CAPTCHAs found after form fill")
        
        # Validate page is still open before proceeding to submission
        try:
            if not playwright_manager.page:
                ultra_safe_log_print("⚠️  Page is None after CAPTCHA re-check")
            elif playwright_manager.page.is_closed():
                ultra_safe_log_print("⚠️  Page closed after CAPTCHA re-check - cannot proceed to submission")
            else:
                ultra_safe_log_print("✅ Page is still open, proceeding to form submission")
        except Exception as e:
            ultra_safe_log_print(f"⚠️  Error checking page status: {str(e)[:50]}")
        
        ultra_safe_log_print("")
        
        # Step 6: Form submission (cannot fail)
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [run_ultra_resilient_submission] Step 6: About to submit form\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
                # Extract and inject WPForms fields before submission
        try:
            # Re-extract WPForms fields to get updated end_timestamp
            # Use form_load_timestamp from earlier in the function (captured at navigation)
            wpforms_data = await extract_wpforms_fields(playwright_manager.page, form_load_timestamp)
            
            if wpforms_data.get('is_wpforms'):
                ultra_safe_log_print("🔑 WPForms detected - preparing form submission")
                
                # Update end_timestamp to current time
                wpforms_data['end_timestamp'] = int(time.time())
                
                # Inject all WPForms fields into the form DOM
                injection_success = await inject_wpforms_fields(playwright_manager.page, wpforms_data)
                
                # Also store WPForms data in JavaScript global for AJAX interception
                # And intercept WPForms submit handler directly
                await playwright_manager.page.evaluate("""
                    (wpformsData) => {
                        window.__wpformsData = wpformsData;
                        
                        // Intercept WPForms submit handler if it exists
                        if (window.wpforms && window.wpforms.submitForm) {
                            const originalSubmit = window.wpforms.submitForm;
                            window.wpforms.submitForm = function(formId, $form) {
                                // Inject WPForms fields before submission
                                const form = $form && $form[0] ? $form[0] : document.querySelector('form[data-formid="' + formId + '"]');
                                if (form) {
                                    // Ensure all WPForms fields are in the form
                                    if (wpformsData.token) {
                                        let tokenInput = form.querySelector('input[name="wpforms[token]"]');
                                        if (!tokenInput) {
                                            tokenInput = document.createElement('input');
                                            tokenInput.type = 'hidden';
                                            tokenInput.name = 'wpforms[token]';
                                            form.appendChild(tokenInput);
                                        }
                                        tokenInput.value = wpformsData.token;
                                    }
                                    if (wpformsData.start_timestamp) {
                                        let startInput = form.querySelector('input[name="start_timestamp"]');
                                        if (!startInput) {
                                            startInput = document.createElement('input');
                                            startInput.type = 'hidden';
                                            startInput.name = 'start_timestamp';
                                            form.appendChild(startInput);
                                        }
                                        startInput.value = wpformsData.start_timestamp.toString();
                                    }
                                    if (wpformsData.end_timestamp) {
                                        let endInput = form.querySelector('input[name="end_timestamp"]');
                                        if (!endInput) {
                                            endInput = document.createElement('input');
                                            endInput.type = 'hidden';
                                            endInput.name = 'end_timestamp';
                                            form.appendChild(endInput);
                                        }
                                        endInput.value = wpformsData.end_timestamp.toString();
                                    }
                                    if (wpformsData.form_id) {
                                        let formIdInput = form.querySelector('input[name="wpforms[id]"]');
                                        if (!formIdInput) {
                                            formIdInput = document.createElement('input');
                                            formIdInput.type = 'hidden';
                                            formIdInput.name = 'wpforms[id]';
                                            form.appendChild(formIdInput);
                                        }
                                        formIdInput.value = wpformsData.form_id;
                                    }
                                    if (wpformsData.submit) {
                                        let submitInput = form.querySelector('input[name="wpforms[submit]"]');
                                        if (!submitInput) {
                                            submitInput = document.createElement('input');
                                            submitInput.type = 'hidden';
                                            submitInput.name = 'wpforms[submit]';
                                            form.appendChild(submitInput);
                                        }
                                        submitInput.value = wpformsData.submit;
                                    }
                                }
                                return originalSubmit.apply(this, arguments);
                            };
                        }
                        
                        // Also intercept jQuery form submit if WPForms uses it
                        if (window.jQuery && window.jQuery.fn) {
                            const $ = window.jQuery;
                            const originalSerialize = $.fn.serialize;
                            $.fn.serialize = function() {
                                const form = this[0];
                                if (form && form.tagName === 'FORM' && form.classList.contains('wpforms-form')) {
                                    // Ensure WPForms fields are in form before serialization
                                    if (wpformsData.token) {
                                        let tokenInput = form.querySelector('input[name="wpforms[token]"]');
                                        if (!tokenInput) {
                                            tokenInput = document.createElement('input');
                                            tokenInput.type = 'hidden';
                                            tokenInput.name = 'wpforms[token]';
                                            form.appendChild(tokenInput);
                                        }
                                        tokenInput.value = wpformsData.token;
                                    }
                                    if (wpformsData.start_timestamp) {
                                        let startInput = form.querySelector('input[name="start_timestamp"]');
                                        if (!startInput) {
                                            startInput = document.createElement('input');
                                            startInput.type = 'hidden';
                                            startInput.name = 'start_timestamp';
                                            form.appendChild(startInput);
                                        }
                                        startInput.value = wpformsData.start_timestamp.toString();
                                    }
                                    if (wpformsData.end_timestamp) {
                                        let endInput = form.querySelector('input[name="end_timestamp"]');
                                        if (!endInput) {
                                            endInput = document.createElement('input');
                                            endInput.type = 'hidden';
                                            endInput.name = 'end_timestamp';
                                            form.appendChild(endInput);
                                        }
                                        endInput.value = wpformsData.end_timestamp.toString();
                                    }
                                }
                                return originalSerialize.apply(this, arguments);
                            };
                        }
                    }
                """, wpforms_data)
                
                if injection_success:
                    ultra_safe_log_print("   ✅ WPForms fields injected:")
                    if wpforms_data.get('token'):
                        ultra_safe_log_print(f"      🔑 wpforms[token]: {wpforms_data['token'][:20]}...")
                    if wpforms_data.get('start_timestamp'):
                        ultra_safe_log_print(f"      ⏰ start_timestamp: {wpforms_data['start_timestamp']}")
                    if wpforms_data.get('end_timestamp'):
                        ultra_safe_log_print(f"      ⏰ end_timestamp: {wpforms_data['end_timestamp']}")
                    if wpforms_data.get('form_id'):
                        ultra_safe_log_print(f"      📋 wpforms[id]: {wpforms_data['form_id']}")
                    if wpforms_data.get('submit'):
                        ultra_safe_log_print(f"      📤 wpforms[submit]: {wpforms_data['submit']}")
                else:
                    ultra_safe_log_print("   ⚠️  Failed to inject WPForms fields")
            else:
                ultra_safe_log_print("   ℹ️  Not a WPForms form (or WPForms not detected)")
        except Exception as e:
            ultra_safe_log_print(f"   ⚠️  Could not prepare WPForms fields: {str(e)[:50]}")
        
        ultra_safe_log_print("📤 STEP 6: Submitting form...")
        ultra_safe_log_print("-" * 80)
        
        # Ensure form submission happens even if CAPTCHA solving failed
        # Validate page is still open before submission
        page_valid = True
        try:
            if not playwright_manager.page:
                page_valid = False
                ultra_safe_log_print("⚠️  Page is None, cannot submit form")
            elif playwright_manager.page.is_closed():
                page_valid = False
                ultra_safe_log_print("⚠️  Page is closed, cannot submit form")
        except Exception as e:
            ultra_safe_log_print(f"⚠️  Cannot verify page status: {str(e)[:50]}")
            page_valid = False
        
        if not page_valid:
            ultra_safe_log_print("⚠️  Cannot submit form - page is not available")
            result["submission_attempted"] = False
            result["submission_success"] = False
            result["error"] = "Page closed or unavailable"
        else:
            # Always attempt submission at least once, even if CAPTCHA solving failed
            ultra_safe_log_print("🔄 Attempting form submission (will proceed even if CAPTCHA solving failed)...")
            
            # First, try the normal submission flow with timeout
            submit_result = None
            try:
                submit_result = await asyncio.wait_for(
                    ultra_simple_form_submit(playwright_manager.page),
                    timeout=30.0  # 30 second timeout for submission
                )
                result.update(submit_result)
                result["steps_completed"].append("submission_attempted")
                ultra_safe_log_print(f"✅ Form submission attempted: {submit_result.get('submission_attempted', False)}")
            except asyncio.TimeoutError:
                ultra_safe_log_print("⚠️  Form submission timed out (30s), trying direct button click...")
                submit_result = {"submission_attempted": False}
            except Exception as e:
                error_msg = str(e)
                ultra_safe_log_print(f"⚠️  Form submission error: {error_msg[:50]}")
                submit_result = {"submission_attempted": False}
            
            # If submission wasn't attempted, try direct button click
            if not submit_result or not submit_result.get("submission_attempted"):
                ultra_safe_log_print("   ⚠️  Normal submission didn't work, trying direct button click...")
                try:
                    # Validate page is still open
                    if playwright_manager.page and not playwright_manager.page.is_closed():
                        submit_button = await playwright_manager.page.query_selector('button[type="submit"], input[type="submit"], button:has-text("Submit"), button:has-text("Send"), form button:not([type="button"])')
                        if submit_button:
                            ultra_safe_log_print("   ✅ Submit button found, clicking...")
                            await submit_button.click(timeout=10000)
                            ultra_safe_log_print("   ✅ Submit button clicked directly")
                            result["submission_attempted"] = True
                            await asyncio.sleep(2)
                        else:
                            ultra_safe_log_print("   ⚠️  Submit button not found, trying form.submit()...")
                            # Try form.submit() as last resort
                            await playwright_manager.page.evaluate("() => { const form = document.querySelector('form'); if (form) form.submit(); }")
                            ultra_safe_log_print("   ✅ Form submitted via form.submit()")
                            result["submission_attempted"] = True
                            await asyncio.sleep(2)
                    else:
                        ultra_safe_log_print("   ⚠️  Page is closed, cannot click submit button")
                except Exception as e:
                    ultra_safe_log_print(f"   ⚠️  Direct submission attempt failed: {str(e)[:50]}")
                    # Still mark as attempted
                    result["submission_attempted"] = True
                    result["submission_success"] = False
                    result["error"] = str(e)[:100]
        
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [run_ultra_resilient_submission] Step 6: Form submission completed\n")
                    f.write(f"📍 [run_ultra_resilient_submission] Submission attempted: {submit_result.get('submission_attempted', False)}\n")
                    f.write(f"📍 [run_ultra_resilient_submission] Submission detected: {submit_result.get('form_submission_detected', False)}\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        ultra_safe_log_print(f"✅ Submission step completed")
        ultra_safe_log_print(f"   - Attempted: {submit_result.get('submission_attempted', False)}")
        ultra_safe_log_print(f"   - Detected: {submit_result.get('form_submission_detected', False)}")
        ultra_safe_log_print(f"   - Success flag: {submit_result.get('submission_success', False)}")
        ultra_safe_log_print(f"   - POST requests: {submit_result.get('post_requests', 0)}")
        ultra_safe_log_print(f"   - Form data captured: {submit_result.get('form_submission_data') is not None}")
        ultra_safe_log_print("")
        
        # Collect all logs for final message - DETAILED VERSION
        all_logs = []
        all_logs.append("=" * 80)
        all_logs.append("AUTOMATION EXECUTION LOG - DETAILED")
        all_logs.append("=" * 80)
        all_logs.append(f"URL: {url}")
        all_logs.append(f"Template: {template.get('name', 'Universal Auto-Detect')}")
        all_logs.append(f"Template Type: {result.get('template_used', 'unknown')}")
        all_logs.append(f"Headless Mode: {headless_mode}")
        all_logs.append("")
        all_logs.append("STEPS COMPLETED:")
        for step in result.get('steps_completed', []):
            all_logs.append(f"  ✅ {step}")
        all_logs.append("")
        
        # Add form filling details
        all_logs.append("FORM FILLING:")
        fields_filled = result.get("fields_filled", 0)
        fields_attempted = result.get("fields_attempted", 0)
        all_logs.append(f"  Fields attempted: {fields_attempted}")
        all_logs.append(f"  Fields filled: {fields_filled}")
        if fields_filled == 0:
            all_logs.append("  ⚠️  WARNING: No form fields were filled!")
        all_logs.append("")
        
        # Add CAPTCHA details
        all_logs.append("CAPTCHA HANDLING:")
        captcha_result = result.get("captcha_result", {})
        captchas_detected = captcha_result.get("captchas_detected", 0)
        captchas_solved = captcha_result.get("captchas_solved", 0)
        all_logs.append(f"  CAPTCHAs detected: {captchas_detected}")
        all_logs.append(f"  CAPTCHAs solved: {captchas_solved}")
        if captchas_detected > 0 and captchas_solved == 0:
            all_logs.append("  ⚠️  WARNING: CAPTCHAs detected but NOT solved!")
        elif captchas_detected == 0:
            all_logs.append("  ℹ️  No CAPTCHAs detected on page")
        all_logs.append("")
        
        # Add submission details
        all_logs.append("SUBMISSION DETAILS:")
        all_logs.append(f"  Submission attempted: {submit_result.get('submission_attempted', False)}")
        all_logs.append(f"  Form submission detected: {submit_result.get('form_submission_detected', False)}")
        all_logs.append(f"  Submission success: {submit_result.get('submission_success', False)}")
        all_logs.append(f"  Method used: {submit_result.get('method_used', 'none')}")
        all_logs.append(f"  POST requests: {submit_result.get('post_requests', 0)}")
        all_logs.append(f"  POST responses: {submit_result.get('post_responses', 0)}")
        all_logs.append(f"  GET requests: {submit_result.get('get_requests', 0)}")
        
        form_submission_data = submit_result.get("form_submission_data")
        if form_submission_data:
            all_logs.append(f"  ✅ Form data verified in request")
            if isinstance(form_submission_data, dict):
                all_logs.append(f"     URL: {form_submission_data.get('url', 'unknown')[:80]}")
                if form_submission_data.get('data_preview'):
                    all_logs.append(f"     Data preview: {form_submission_data.get('data_preview', '')[:200]}")
        else:
            all_logs.append(f"  ⚠️  WARNING: No form data captured in request!")
            all_logs.append(f"     This may indicate the form was NOT actually submitted.")
        
        all_logs.append("")
        all_logs.append("FINAL VERIFICATION:")
        has_form_data = submit_result.get("form_submission_data") is not None
        form_detected = submit_result.get("form_submission_detected", False)
        submission_success = submit_result.get("submission_success", False)
        
        all_logs.append(f"  Form submission detected: {form_detected}")
        all_logs.append(f"  Form data verified: {has_form_data}")
        all_logs.append(f"  Submission success flag: {submission_success}")
        
        if submission_success and not has_form_data:
            all_logs.append("  ⚠️  WARNING: Marked as success but NO form data verified!")
            all_logs.append("     This is likely a FALSE POSITIVE - form may not have actually submitted.")
        elif submission_success and has_form_data:
            all_logs.append("  ✅ All verification checks passed - submission confirmed.")
        elif not submission_success:
            all_logs.append("  ❌ Submission verification failed.")
        
        all_logs.append("")
        all_logs.append("=" * 80)
        
        # Get field filling stats for status determination
        fields_filled = result.get("fields_filled", 0)
        fields_attempted = result.get("fields_attempted", 0)
        
        # Determine final status - STRICT verification
        # CRITICAL: Only mark as success if fields were filled AND submission was verified
        if submit_result.get("submission_success") and submit_result.get("form_submission_detected"):
            # Only mark as success if BOTH submission_success AND form_submission_detected are True
            # AND we have form_submission_data
            # AND fields were actually filled
            has_form_data = submit_result.get("form_submission_data") is not None
            if has_form_data and fields_filled > 0:
                all_logs.append("✅ FINAL STATUS: SUCCESS - Form submitted with verified data")
                result.update({
                    "status": "success",
                    "message": "\n".join(all_logs)
                })
            elif has_form_data and fields_filled == 0:
                # Has form data but no fields filled - suspicious, mark as failed
                all_logs.append("❌ FINAL STATUS: FAILED - Form data captured but no fields were filled")
                result.update({
                    "status": "failed",
                    "message": "\n".join(all_logs)
                })
            else:
                # No form data verification - mark as failed
                all_logs.append("❌ FINAL STATUS: FAILED - No form data verification")
                result.update({
                    "status": "failed",
                    "message": "\n".join(all_logs)
                })
        elif submit_result.get("submission_attempted"):
            # Submission was attempted but not verified
            # Check if fields were filled and submission was detected
            form_detected = submit_result.get("form_submission_detected", False)
            has_form_data = submit_result.get("form_submission_data") is not None
            
            if fields_filled == 0 and fields_attempted == 0:
                # No fields filled at all - this is a failure
                all_logs.append("❌ FINAL STATUS: FAILED - No fields filled and no submission verified")
                result.update({
                    "status": "failed",
                    "message": "\n".join(all_logs)
                })
            elif not form_detected and not has_form_data:
                # Submission attempted but not detected - failure
                all_logs.append("❌ FINAL STATUS: FAILED - Submission attempted but not detected")
                result.update({
                    "status": "failed",
                    "message": "\n".join(all_logs)
                })
            else:
                # Some fields filled but submission not fully verified - unconfirmed
                all_logs.append("⚠️  FINAL STATUS: SUBMITTED (unconfirmed) - Submission attempted but not verified")
                result.update({
                    "status": "submitted",
                    "message": "\n".join(all_logs)
                })
        else:
            # No submission was attempted
            if fields_filled == 0:
                all_logs.append("❌ FINAL STATUS: FAILED - No fields filled and no submission attempted")
            else:
                all_logs.append("❌ FINAL STATUS: FAILED - No submission was attempted")
            result.update({
                "status": "failed",
                "message": "\n".join(all_logs)
            })
        
        ultra_safe_log_print("✅ Process completed successfully")
        ultra_safe_log_print("\n".join(all_logs))
        
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [run_ultra_resilient_submission] Process completed, status: {result.get('status', 'unknown')}\n")
                    f.write("📍 [run_ultra_resilient_submission] About to return result\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        return result
        
    except Exception as e:
        # This should never happen, but just in case
        error_msg = str(e)[:100] if str(e) else "unknown error"
        ultra_safe_log_print(f"💥 Unexpected error in main process: {error_msg}")
        
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [run_ultra_resilient_submission] EXCEPTION: {type(e).__name__}: {error_msg}\n")
                    f.write("📍 [run_ultra_resilient_submission] Creating error result\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        result.update({
            "status": "error",
            "message": f"Unexpected error: {error_msg}",
            "error_type": "unexpected_error",
            "recovered": True
        })
        return result
        
    finally:
        # ULTRA-RESILIENT cleanup (cannot fail)
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [run_ultra_resilient_submission] Finally block: About to cleanup\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        # Check if we're in the middle of CAPTCHA solving before cleanup
        try:
            is_solving_captcha = await playwright_manager.page.evaluate("""
                () => {
                    // Check if CAPTCHA challenge iframe is still present
                    const challengeIframes = document.querySelectorAll('iframe[title*="challenge"], iframe[src*="bframe"]');
                    if (challengeIframes.length > 0) {
                        return true;
                    }
                    // Check if we're waiting for token
                    const recaptchaResponse = document.querySelector('#g-recaptcha-response');
                    if (recaptchaResponse && (!recaptchaResponse.value || recaptchaResponse.value.length < 20)) {
                        return true; // Still waiting for token
                    }
                    return false;
                }
            """) if playwright_manager.page and not playwright_manager.page.is_closed() else False
        except:
            is_solving_captcha = False
        
        if is_solving_captcha:
            ultra_safe_log_print("⚠️  CAPTCHA solving still in progress, waiting a bit longer before cleanup...")
            await asyncio.sleep(5)  # Give it a bit more time
        
        ultra_safe_log_print("🔒 Cleaning up resources...")
        await UltimateSafetyWrapper.execute_async(
            playwright_manager.cleanup,
            default_return=None
        )
        ultra_safe_log_print("🔒 Cleanup completed")
        
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [run_ultra_resilient_submission] Cleanup completed\n")
                    f.write("📍 [run_ultra_resilient_submission] Function exit\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass

async def main_async_with_ultimate_safety(args: argparse.Namespace) -> str:
    """ULTRA-RESILIENT main async function - CANNOT FAIL to return JSON."""
    
    # Initialize heartbeat file path for debugging (available throughout function)
    heartbeat_file_path = None
    try:
        heartbeat_file_path = Path('/var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_script_heartbeat_' + str(os.getpid()) + '.txt')
        if not heartbeat_file_path.exists():
            heartbeat_file_path = Path('/tmp/python_script_heartbeat_' + str(os.getpid()) + '.txt')
    except:
        pass
    
    # Update heartbeat immediately - function entry
    try:
        if heartbeat_file_path and heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write("📍 [main_async] Function entry - main_async_with_ultimate_safety called\n")
                f.write("📍 [main_async] Function called\n")
                f.write("📍 [main_async] About to write startup messages\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    # Use non-blocking stderr writes to prevent hanging on full pipe buffers
    # CRITICAL: Even sys.stderr.write() can block if pipe buffer is full!
    # Solution: Check if pipe is writable before writing, skip if not
    try:
        import select
        import errno
        HAS_SELECT = True
    except ImportError:
        HAS_SELECT = False
        import errno
    
    def safe_write(msg):
        """Write to stderr without blocking - skip if pipe buffer is full."""
        try:
            # Check if stderr is a pipe (not TTY)
            is_pipe = not (hasattr(sys.stderr, 'isatty') and sys.stderr.isatty())
            
            if is_pipe and HAS_SELECT:
                # For pipes, check if writable before writing (non-blocking check)
                try:
                    if hasattr(sys.stderr, 'fileno'):
                        fileno = sys.stderr.fileno()
                        # Check if file descriptor is writable (timeout 0 = non-blocking)
                        # If not writable, pipe buffer is full - skip to avoid blocking
                        ready, _, _ = select.select([], [fileno], [], 0)
                        if fileno not in ready:
                            # Pipe buffer is full, skip this write to avoid blocking
                            # This is OK - Node.js will eventually read and we'll continue
                            return
                except (OSError, ValueError):
                    # select failed (might be Windows or other issue), try writing anyway
                    pass
            
            # Write the message (this might still block, but we tried to prevent it)
            try:
                sys.stderr.write(msg)
            except (IOError, OSError) as e:
                # If write would block (EAGAIN/EWOULDBLOCK), just skip it
                if hasattr(errno, 'EAGAIN') and e.errno == errno.EAGAIN:
                    return
                if hasattr(errno, 'EWOULDBLOCK') and e.errno == errno.EWOULDBLOCK:
                    return
                # Other error, continue silently
            
            # Only flush if it's a TTY (terminal), not a pipe
            if not is_pipe:
                try:
                    if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
                        sys.stderr.flush()
                except:
                    pass
        except:
            # Any error - silently skip to prevent blocking
            pass
    
    # CRITICAL: Update heartbeat FIRST before any stderr writes (heartbeat_file_path already initialized above)
    try:
        if heartbeat_file_path and heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write("📍 [main_async] About to write startup messages (duplicate check)\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    # Try to write to stderr, but don't let it block execution
    safe_write("📍 [main_async] Function called\n")
    
    # Print startup logs - but skip if pipe might be blocking
    # CRITICAL: Don't let logging block execution!
    try:
        safe_write("=" * 80 + "\n")
        safe_write("🚀 AUTOMATION STARTING\n")
        safe_write("=" * 80 + "\n")
        timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S')
        safe_write(f"Timestamp: {timestamp_str}\n")
    except Exception as e:
        # If write fails, just continue - don't block
        pass
    
    # Update heartbeat to show we got past the writes
    try:
        if heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write("📍 [main_async] After initial log prints\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    safe_write("📍 [main_async] After initial log prints\n")
    
    # Update heartbeat
    try:
        if heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write("📍 [main_async] About to get URL\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    # Validate inputs with fallbacks
    safe_write("📍 [main_async] About to get URL\n")
    
    url = UltimateSafetyWrapper.execute_sync(
        lambda: args.url if hasattr(args, 'url') and args.url else "https://example.com",
        default_return="https://example.com"
    )
    
    # Update heartbeat
    try:
        if heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write(f"📍 [main_async] URL: {url}\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    safe_write(f"📍 [main_async] URL: {url}\n")
    safe_write(f"📋 Target URL: {url}\n")
    
    # Try ultra_safe_log_print but don't let it block
    try:
        ultra_safe_log_print(f"📋 Target URL: {url}")
    except:
        pass
    
    # Update heartbeat
    try:
        if heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write("📍 [main_async] About to get template path\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    safe_write("📍 [main_async] About to get template path\n")
    
    template_path = UltimateSafetyWrapper.execute_sync(
        lambda: Path(args.template) if hasattr(args, 'template') and args.template else Path("default.json"),
        default_return=Path("default.json")
    )
    
    # Update heartbeat
    try:
        if heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write(f"📍 [main_async] Template path: {template_path}\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    safe_write(f"📍 [main_async] Template path: {template_path}\n")
    safe_write(f"📄 Template path: {template_path}\n")
    safe_write("\n")
    
    # Try ultra_safe_log_print but don't let it block
    try:
        ultra_safe_log_print(f"📄 Template path: {template_path}")
        ultra_safe_log_print("")
    except:
        pass
    
    # Update heartbeat - about to read template
    try:
        if heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write("📍 [main_async] About to read template file\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    try:
        # Get timeout from template or use default
        template_content = UltimateSafetyWrapper.execute_sync(
            template_path.read_text,
            encoding='utf-8',
            default_return='{}'
        )
        
        template_data = UltimateSafetyWrapper.execute_sync(
            json.loads,
            template_content,
            default_return={}
        )
        
        timeout = template_data.get("max_timeout_seconds", 300)
        
        # Update heartbeat - template read successfully
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [main_async] Template read, timeout: {timeout}s\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
    except Exception as e:
        timeout = 300
        # Update heartbeat - template read failed, using default
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [main_async] Template read failed, using default timeout: {timeout}s\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
    
    # Update heartbeat - about to start submission
    try:
        if heartbeat_file_path.exists():
            with open(heartbeat_file_path, 'a') as f:
                f.write(f"📍 [main_async] Starting submission with timeout: {timeout} seconds\n")
                f.flush()
                os.fsync(f.fileno())
    except:
        pass
    
    # Run with timeout protection and multiple fallbacks
    try:
        ultra_safe_log_print(f"⏱️  Starting submission with timeout: {timeout} seconds")
        ultra_safe_log_print("")
        
        # Update heartbeat - about to call run_ultra_resilient_submission
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [main_async] About to call run_ultra_resilient_submission\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        # Wrap in retry loop for rate limit errors - restart entire process
        max_restarts = 2
        result = None
        for restart_attempt in range(max_restarts + 1):
            try:
                result = await asyncio.wait_for(
                    run_ultra_resilient_submission(url, template_path),
                    timeout=timeout
                )
                break  # Success, exit retry loop
            except Exception as e:
                error_msg = str(e)
                if "RECAPTCHA_RATE_LIMIT_RESTART_FULL" in error_msg and restart_attempt < max_restarts:
                    ultra_safe_log_print(f"   ⚠️  Rate limit detected, restarting entire process (attempt {restart_attempt + 1}/{max_restarts + 1})")
                    wait_time = 10 + (restart_attempt * 5)  # 10s, 15s, etc.
                    ultra_safe_log_print(f"   ⏳ Waiting {wait_time} seconds before full restart...")
                    await asyncio.sleep(wait_time)
                    ultra_safe_log_print("   🔄 Restarting from beginning (form finding, CAPTCHA clicking, etc.)...")
                    continue  # Retry from beginning
                else:
                    # Other error or max retries reached, re-raise
                    raise
        
        # Update heartbeat - submission completed
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [main_async] Submission completed, status: {result.get('status', 'unknown')}\n")
                    f.write("📍 [main_async] About to process result\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        ultra_safe_log_print("")
        ultra_safe_log_print("=" * 80)
        ultra_safe_log_print("📊 SUBMISSION PROCESS COMPLETED")
        ultra_safe_log_print("=" * 80)
        
        # Update heartbeat - processing result
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [main_async] Processing result format\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        # Ensure result is properly formatted
        if not isinstance(result, dict):
            ultra_safe_log_print("⚠️  Invalid result format, creating fallback")
            result = {"status": "error", "message": "Invalid result format", "recovered": True}
            
        result["url"] = url  # Ensure URL is always set
        result["timestamp"] = time.time()
        
        # Update heartbeat - result formatted
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [main_async] Result formatted, status: {result.get('status', 'unknown')}\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        # Print final result summary
        ultra_safe_log_print(f"Final Status: {result.get('status', 'unknown')}")
        message_length = len(result.get('message', ''))
        ultra_safe_log_print(f"Message length: {message_length} characters")
        
        # ALWAYS ensure message contains detailed logs - this is critical
        if not result.get("message") or message_length < 200:
            ultra_safe_log_print("⚠️  WARNING: Result message is too short or missing, adding detailed info")
            detailed_logs = []
            detailed_logs.append("=" * 80)
            detailed_logs.append("AUTOMATION EXECUTION LOG - DETAILED")
            detailed_logs.append("=" * 80)
            detailed_logs.append(f"URL: {url}")
            detailed_logs.append(f"Template: {template_data.get('name', 'Universal Auto-Detect')}")
            detailed_logs.append(f"Status: {result.get('status', 'unknown')}")
            detailed_logs.append(f"Steps completed: {', '.join(result.get('steps_completed', []))}")
            detailed_logs.append(f"Fields filled: {result.get('fields_filled', 0)}")
            detailed_logs.append(f"Fields attempted: {result.get('fields_attempted', 0)}")
            detailed_logs.append(f"CAPTCHAs detected: {result.get('captcha_result', {}).get('captchas_detected', 0)}")
            detailed_logs.append(f"CAPTCHAs solved: {result.get('captcha_result', {}).get('captchas_solved', 0)}")
            detailed_logs.append(f"Submission attempted: {result.get('submission_attempted', False)}")
            detailed_logs.append(f"Form submission detected: {result.get('form_submission_detected', False)}")
            detailed_logs.append(f"Submission success: {result.get('submission_success', False)}")
            detailed_logs.append(f"POST requests: {result.get('post_requests', 0)}")
            detailed_logs.append(f"POST responses: {result.get('post_responses', 0)}")
            detailed_logs.append("=" * 80)
            
            if result.get("message"):
                result["message"] = "\n".join(detailed_logs) + "\n\n" + result["message"]
            else:
                result["message"] = "\n".join(detailed_logs)
        
        ultra_safe_log_print("")
        ultra_safe_log_print("📋 Final message preview (first 500 chars):")
        ultra_safe_log_print(result.get("message", "")[:500])
        ultra_safe_log_print("")
        
        # Update heartbeat - about to output JSON
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [main_async] About to output JSON result\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        # Print JSON result to stdout (for route.ts to capture)
        json_result = json.dumps(result, indent=2)
        ultra_safe_log_print("📤 Outputting JSON result to stdout...")
        print(json_result, flush=True)  # Print to stdout for route.ts
        ultra_safe_log_print("✅ JSON result output complete")
        
        # Update heartbeat - JSON output complete
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [main_async] JSON result output complete\n")
                    f.write("📍 [main_async] About to return json_result\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        return json_result
        
    except asyncio.TimeoutError:
        # Update heartbeat - timeout occurred
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [main_async] TIMEOUT ERROR after {timeout} seconds\n")
                    f.write("📍 [main_async] Creating timeout result\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        # Try to read heartbeat file to get logs
        captured_logs = []
        try:
            if heartbeat_file_path and heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'r') as f:
                    captured_logs = f.readlines()
        except:
            pass
        
        ultra_safe_log_print("")
        ultra_safe_log_print("⏱️  TIMEOUT: Operation exceeded timeout")
        ultra_safe_log_print(f"⏱️  Timeout occurred after {timeout} seconds")
        ultra_safe_log_print("")
        ultra_safe_log_print("=" * 80)
        ultra_safe_log_print("TIMEOUT SUMMARY")
        ultra_safe_log_print("=" * 80)
        ultra_safe_log_print(f"URL: {url}")
        ultra_safe_log_print(f"Timeout: {timeout} seconds")
        ultra_safe_log_print("")
        ultra_safe_log_print("⚠️  The automation process exceeded the timeout limit.")
        ultra_safe_log_print("   This usually happens when:")
        ultra_safe_log_print("   1. CAPTCHA solving takes too long")
        ultra_safe_log_print("   2. Page loading is very slow")
        ultra_safe_log_print("   3. Network issues")
        ultra_safe_log_print("")
        if captured_logs:
            ultra_safe_log_print("Last known progress (from heartbeat):")
            # Get last 20 lines of heartbeat
            last_lines = captured_logs[-20:] if len(captured_logs) > 20 else captured_logs
            for line in last_lines:
                if line.strip():
                    ultra_safe_log_print(f"   {line.strip()}")
        ultra_safe_log_print("")
        ultra_safe_log_print("=" * 80)
        
        # Build timeout message with captured info
        timeout_message = f"Operation timed out after {timeout} seconds\n\n"
        timeout_message += "=" * 80 + "\n"
        timeout_message += "TIMEOUT SUMMARY\n"
        timeout_message += "=" * 80 + "\n"
        timeout_message += f"URL: {url}\n"
        timeout_message += f"Timeout: {timeout} seconds\n\n"
        timeout_message += "⚠️  The automation process exceeded the timeout limit.\n"
        timeout_message += "   This usually happens when:\n"
        timeout_message += "   1. CAPTCHA solving takes too long (audio challenge requires ffmpeg/ffprobe)\n"
        timeout_message += "   2. Page loading is very slow\n"
        timeout_message += "   3. Network issues\n\n"
        timeout_message += "💡 COMMON FIXES:\n"
        timeout_message += "   - Install ffmpeg for audio CAPTCHA solving: sudo apt-get install -y ffmpeg\n"
        timeout_message += "   - Check if ffmpeg is in PATH: which ffmpeg && which ffprobe\n"
        timeout_message += "   - Increase timeout in template if needed\n\n"
        if captured_logs:
            timeout_message += "Last known progress (from heartbeat):\n"
            last_lines = captured_logs[-30:] if len(captured_logs) > 30 else captured_logs
            for line in last_lines:
                if line.strip():
                    timeout_message += f"   {line.strip()}\n"
        else:
            timeout_message += "ℹ️  Progress logs are available in the submission log above.\n"
        timeout_message += "\n" + "=" * 80 + "\n"
        timeout_message += "💡 TIP: Check the heartbeat file for detailed progress:\n"
        if heartbeat_file_path:
            timeout_message += f"   {heartbeat_file_path}\n"
        timeout_message += "\n📋 NOTE: All execution logs are captured in stderr and displayed above.\n"
        
        timeout_result = {
            "status": "timeout",
            "message": timeout_message,
            "url": url,
            "error_type": "timeout",
            "recovered": True,
            "timestamp": time.time()
        }
        
        # Update heartbeat - timeout result created
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [main_async] Timeout result created, about to output JSON\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        json_result = json.dumps(timeout_result)
        print(json_result, flush=True)
        
        # Update heartbeat - timeout JSON output
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [main_async] Timeout JSON output, returning\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        return json_result
        
    except Exception as e:
        # Update heartbeat - exception occurred
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write(f"📍 [main_async] EXCEPTION: {type(e).__name__}: {str(e)[:100]}\n")
                    f.write("📍 [main_async] Creating error result\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        error_msg = str(e)
        ultra_safe_log_print("")
        ultra_safe_log_print(f"❌ ERROR: {error_msg}")
        import traceback
        traceback_str = traceback.format_exc()
        ultra_safe_log_print(f"Traceback:\n{traceback_str}")
        
        error_result = {
            "status": "error",
            "message": f"Execution failed: {error_msg}\n\nTraceback:\n{traceback_str}",
            "url": url,
            "error_type": "execution_failed",
            "recovered": True,
            "timestamp": time.time()
        }
        
        # Update heartbeat - error result created
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [main_async] Error result created, about to output JSON\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        json_result = json.dumps(error_result)
        print(json_result, flush=True)
        
        # Update heartbeat - error JSON output
        try:
            if heartbeat_file_path.exists():
                with open(heartbeat_file_path, 'a') as f:
                    f.write("📍 [main_async] Error JSON output, returning\n")
                    f.flush()
                    os.fsync(f.fileno())
        except:
            pass
        
        return json_result

def main() -> int:
    """ULTRA-RESILIENT main function - CANNOT FAIL."""
    
    # Ultimate argument parsing with fallbacks
    try:
        parser = argparse.ArgumentParser(description="ULTRA-RESILIENT form automation.", add_help=False)
        parser.add_argument("--url", required=True, help="Target form URL.")
        parser.add_argument("--template", required=True, help="Path to JSON template.")
        
        try:
            args = parser.parse_args()
        except SystemExit:
            # Argument parsing failed, use defaults
            args = argparse.Namespace()
            args.url = "https://example.com"
            args.template = "template.json"
            
    except Exception:
        # Ultimate fallback for argument parsing
        args = argparse.Namespace()
        args.url = "https://example.com"
        args.template = "template.json"
    
    # ULTRA-RESILIENT execution
    try:
        # Update heartbeat before starting main function
        try:
            if heartbeat_file:
                if isinstance(heartbeat_file, Path):
                    if heartbeat_file.exists():
                        with open(heartbeat_file, 'a') as f:
                            f.write("About to call asyncio.run(main_async_with_ultimate_safety)\n")
                            f.flush()
                            os.fsync(f.fileno())
                else:
                    if os.path.exists(str(heartbeat_file)):
                        with open(heartbeat_file, 'a') as f:
                            f.write("About to call asyncio.run(main_async_with_ultimate_safety)\n")
                            f.flush()
                            os.fsync(f.fileno())
        except:
            pass
        
        sys.stderr.write("📍 [main()] About to call asyncio.run(main_async_with_ultimate_safety)\n")
        sys.stderr.flush()
        
        # Run the async function and get JSON result
        json_result = asyncio.run(main_async_with_ultimate_safety(args))
        
        sys.stderr.write("📍 [main()] asyncio.run() completed\n")
        sys.stderr.flush()
        
        # Update heartbeat after main function
        try:
            if heartbeat_file:
                if isinstance(heartbeat_file, Path):
                    if heartbeat_file.exists():
                        with open(heartbeat_file, 'a') as f:
                            f.write("asyncio.run() completed\n")
                            f.flush()
                            os.fsync(f.fileno())
                else:
                    if os.path.exists(str(heartbeat_file)):
                        with open(heartbeat_file, 'a') as f:
                            f.write("asyncio.run() completed\n")
                            f.flush()
                            os.fsync(f.fileno())
        except:
            pass
        
        # ULTRA-RESILIENT output - cannot fail
        try:
            # Validate JSON before printing
            parsed = json.loads(json_result)
            final_output = json.dumps(parsed)
        except:
            # If JSON is invalid, use fallback
            final_output = get_ultimate_fallback_result(args.url)
        
        # ULTRA-RESILIENT print - cannot fail
        for attempt in range(3):
            try:
                print(final_output)
                break
            except Exception:
                if attempt == 2:
                    # Last resort - write to file
                    try:
                        with open('result.json', 'w', encoding='utf-8') as f:
                            f.write(final_output)
                    except:
                        pass  # Give up silently
                
        # Return success code (always 0 to prevent external failures)
        return 0
        
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        interrupt_result = {
            "status": "interrupted",
            "message": "Process interrupted by user",
            "url": getattr(args, 'url', 'unknown'),
            "error_type": "keyboard_interrupt",
            "recovered": True,
            "timestamp": time.time()
        }
        print(json.dumps(interrupt_result))
        return 0  # Always return 0
        
    except Exception as e:
        # This should never happen, but just in case
        print(get_ultimate_fallback_result(getattr(args, 'url', 'unknown')))
        return 0  # Always return 0

if __name__ == "__main__":
    # ULTRA-RESILIENT entry point - CANNOT FAIL
    exit_code = 0
    try:
        exit_code = main()
    except Exception:
        exit_code = 0  # Always return 0
    
    sys.exit(exit_code)