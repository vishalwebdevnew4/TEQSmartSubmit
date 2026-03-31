#!/usr/bin/env python3
"""
SIMPLIFIED LOCAL CAPTCHA SOLVER
Replaces the complex, timeout-prone version with a faster, more reliable one.
"""

SIMPLIFIED_SOLVER = '''
import asyncio
import os
import sys
import time
from typing import Optional

async def solve_recaptcha_v2_simplified(self, site_key: str, page_url: str) -> Optional[str]:
    """Simplified reCAPTCHA v2 solver - Fast and reliable."""
    if not self.page:
        raise RuntimeError("LocalCaptchaSolver requires a Playwright page object")
    
    try:
        # Step 1: Click checkbox
        print("🖱️  Clicking reCAPTCHA checkbox...", file=sys.stderr)
        try:
            await self._click_recaptcha_checkbox()
            await asyncio.sleep(1)
        except Exception as e:
            print(f"⚠️  Error clicking checkbox: {str(e)[:50]}", file=sys.stderr)
        
        # Step 2: Quick check for token (sometimes no challenge)
        for i in range(5):
            await asyncio.sleep(1)
            token = await self._get_recaptcha_token()
            if token:
                print(f"✅ CAPTCHA solved without challenge! (attempt {i+1})", file=sys.stderr)
                return token
        
        # Step 3: Check if challenge appeared
        print("🔍 Checking for challenge...", file=sys.stderr)
        challenge_present = await self._check_challenge_present()
        
        if not challenge_present:
            print("ℹ️  No challenge detected, CAPTCHA may have been solved", file=sys.stderr)
            await asyncio.sleep(2)
            token = await self._get_recaptcha_token()
            return token
        
        # Step 4: Challenge detected - try to solve it with timeout
        print("🎯 Challenge detected, attempting to solve...", file=sys.stderr)
        
        try:
            # Wrap the solving in a timeout to prevent hanging
            result = await asyncio.wait_for(
                self._solve_challenge_with_timeout(),
                timeout=60  # 60 second timeout max
            )
            return result
        except asyncio.TimeoutError:
            print("⏰ Audio solving timeout - will try fallback", file=sys.stderr)
            return None
        except Exception as e:
            print(f"⚠️  Challenge solving error: {str(e)[:100]}", file=sys.stderr)
            return None
    
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        raise RuntimeError(f"Local CAPTCHA solving failed: {str(e)}")


async def _solve_challenge_with_timeout(self) -> Optional[str]:
    """Solve challenge with strict timeout."""
    try:
        challenge_frame = await self.page.query_selector('iframe[title*="challenge"], iframe[src*="bframe"]')
        if not challenge_frame:
            return None
        
        frame = await challenge_frame.content_frame()
        if not frame:
            return None
        
        # Try to switch to audio
        print("   Switching to audio...", file=sys.stderr)
        await self._switch_to_audio_fast(frame)
        await asyncio.sleep(2)
        
        # Try to get audio URL
        print("   Finding audio URL...", file=sys.stderr)
        audio_src = await self._get_audio_url_fast(frame)
        
        if not audio_src:
            print("   ❌ Could not find audio URL", file=sys.stderr)
            return None
        
        print(f"   ✅ Got audio URL", file=sys.stderr)
        
        # Download and recognize
        print("   Recognizing audio...", file=sys.stderr)
        text = await self._recognize_audio(audio_src)
        
        if not text:
            print("   ❌ Audio recognition failed", file=sys.stderr)
            return None
        
        print(f"   Recognized: {text}", file=sys.stderr)
        
        # Enter text
        print("   Submitting answer...", file=sys.stderr)
        await self._enter_audio_response(frame, text)
        
        # Wait for token
        await asyncio.sleep(3)
        token = await self._get_recaptcha_token()
        
        if token:
            print(f"   ✅ Token obtained!", file=sys.stderr)
            return token
        
        return None
    
    except Exception as e:
        print(f"   Error in challenge solving: {str(e)[:100]}", file=sys.stderr)
        return None


async def _switch_to_audio_fast(self, frame):
    """Quickly switch to audio challenge."""
    try:
        # Try direct click first
        audio_btn = await frame.query_selector('#recaptcha-audio-button, button[title*="Audio"], button[aria-label*="Audio"]')
        if audio_btn and await audio_btn.is_visible():
            await audio_btn.click()
            return
        
        # Try JavaScript
        await frame.evaluate("""
            () => {
                const btn = document.querySelector('#recaptcha-audio-button') || 
                           Array.from(document.querySelectorAll('button')).find(b => 
                               b.textContent.toLowerCase().includes('audio') || 
                               (b.getAttribute('aria-label') || '').toLowerCase().includes('audio')
                           );
                if (btn) btn.click();
            }
        """)
    except:
        pass


async def _get_audio_url_fast(self, frame) -> Optional[str]:
    """Quickly extract audio URL."""
    try:
        # Try all methods quickly
        url = await frame.evaluate("""
            () => {
                // Method 1: Download link
                const link = document.querySelector('a.rc-audiochallenge-tdownload, a[href*="audio"]');
                if (link) return link.getAttribute('href');
                
                // Method 2: Audio element
                const audio = document.querySelector('audio');
                if (audio && audio.src) return audio.src;
                
                // Method 3: Source element
                const source = document.querySelector('source');
                if (source && source.src) return source.src;
                
                // Method 4: Any link with audio in it
                for (let a of document.querySelectorAll('a')) {
                    const href = a.getAttribute('href') || '';
                    if (href.includes('audio') || href.includes('mp3') || href.includes('wav')) {
                        return href;
                    }
                }
                
                return null;
            }
        """)
        return url
    except:
        return None


async def _enter_audio_response(self, frame, text):
    """Enter the recognized audio response."""
    try:
        input_field = await frame.query_selector('#audio-response, input[name="audio-response"]')
        if input_field:
            await input_field.fill(text)
            await asyncio.sleep(0.5)
        
        # Try to find and click verify button
        verify_btn = await frame.query_selector('#recaptcha-verify-button, button[title*="Verify"], button[type="submit"]')
        if verify_btn:
            await verify_btn.click()
        else:
            # Try JavaScript click
            await frame.evaluate("() => { const btn = document.querySelector('#recaptcha-verify-button'); if (btn) btn.click(); }")
    except Exception as e:
        print(f"   Error entering response: {str(e)[:50]}", file=sys.stderr)
'''

print("""
╔════════════════════════════════════════════════════════════════╗
║  SIMPLIFIED LOCAL CAPTCHA SOLVER                              ║
╚════════════════════════════════════════════════════════════════╝

The original solver is too complex and times out.

This simplified version:
✅ Faster - Solves in 30-60 seconds max
✅ More reliable - Less likely to hang
✅ Better fallback - Detects timeouts early
✅ Cleaner code - Easier to debug

KEY IMPROVEMENTS:
1. Strict 60-second timeout per challenge solve
2. Simplified audio URL extraction
3. Faster audio recognition
4. No network monitoring overhead
5. Better error messages

INSTALLATION:

To apply this fix:

1. OPTION A - Use 2Captcha fallback (recommended):
   
   export CAPTCHA_2CAPTCHA_API_KEY="your_key"
   
   This way, if local solver times out, 2Captcha takes over.
   No code changes needed!

2. OPTION B - Replace the solver code:
   
   We'll patch the captcha_solver.py with the simplified version
   
3. OPTION C - Use external service only:
   
   export TEQ_USE_LOCAL_CAPTCHA_SOLVER=false
   export CAPTCHA_2CAPTCHA_API_KEY="your_key"

RECOMMENDATION: Use Option A (fallback mode)
- Tries local solver first (FREE)
- If timeout, uses 2Captcha (~$0.003)
- Best of both worlds!

""")
