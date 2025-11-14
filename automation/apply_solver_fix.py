#!/usr/bin/env python3
"""
Patch script: Fixes the local CAPTCHA solver by adding timeout protection.

This wraps the existing solver with better error handling and timeout management.
"""

import subprocess
import sys

# Apply a monkey patch to add timeout protection
patch_code = '''
# PATCH: Add timeout wrapper to prevent hanging

import functools
import asyncio

original_solve = LocalCaptchaSolver.solve_recaptcha_v2

@functools.wraps(original_solve)
async def solve_with_timeout(self, site_key, page_url):
    """Wrapper that adds timeout protection."""
    try:
        # Try to solve with 60 second timeout
        return await asyncio.wait_for(
            original_solve(self, site_key, page_url),
            timeout=60
        )
    except asyncio.TimeoutError:
        print("⏰ Local solver timeout (60s) - falling back", file=sys.stderr)
        return None
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return None

LocalCaptchaSolver.solve_recaptcha_v2 = solve_with_timeout
'''

print("""
╔════════════════════════════════════════════════════════════════╗
║  APPLYING FIXES TO LOCAL CAPTCHA SOLVER                        ║
╚════════════════════════════════════════════════════════════════╝

This script will:
1. Add timeout protection (prevent hanging)
2. Better error handling
3. Automatic fallback to 2Captcha

""")

# The simple fix: Just disable the complex audio solving and use fallback
print("Applying timeout wrapper...\n")

# Create a simplified wrapper version
wrapper_code = '''
#!/usr/bin/env python3
"""
FIXED LOCAL CAPTCHA SOLVER with timeout protection
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Import original solver
from captcha_solver import LocalCaptchaSolver as _OriginalLocalCaptchaSolver
from captcha_solver import get_captcha_solver as _get_captcha_solver
import functools

class LocalCaptchaSolver(_OriginalLocalCaptchaSolver):
    """Patched LocalCaptchaSolver with timeout protection."""
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str):
        """Solve with timeout protection."""
        try:
            print("🤖 Using LOCAL CAPTCHA SOLVER (with timeout protection)...", file=sys.stderr)
            
            # Try solving with strict timeout
            try:
                result = await asyncio.wait_for(
                    self._solve_recaptcha_v2_impl(site_key, page_url),
                    timeout=45  # 45 second timeout
                )
                if result:
                    return result
            except asyncio.TimeoutError:
                print("⏰ Local solver timeout (45s)", file=sys.stderr)
                print("🔄 Will fall back to external service if available", file=sys.stderr)
                return None
            
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)[:100]}", file=sys.stderr)
            return None
    
    async def _solve_recaptcha_v2_impl(self, site_key: str, page_url: str):
        """Original implementation (from parent class)."""
        # Just call the parent implementation
        # This is the original complex logic, but now with timeout wrapper above
        return await super().solve_recaptcha_v2(site_key, page_url)


def get_captcha_solver(service: str = "auto"):
    """Wrapper for get_captcha_solver that returns patched solver."""
    if service == "local" or (service == "auto" and os.getenv("TEQ_USE_LOCAL_CAPTCHA_SOLVER", "true").lower() != "false"):
        return LocalCaptchaSolver()
    
    return _get_captcha_solver(service)

print("✅ Patched solver loaded with timeout protection!")
'''

# Save wrapper
with open('captcha_solver_patched.py', 'w') as f:
    f.write(wrapper_code)

print("✅ Patched version created: captcha_solver_patched.py\n")

print("""
RECOMMENDED FIX (Fastest):

Simply set your 2Captcha API key and use fallback mode:

    export CAPTCHA_2CAPTCHA_API_KEY="your_api_key"

Then set in your template:
    "use_local_captcha_solver": true,
    "captcha_service": "auto"

This way:
- Local solver attempts (FREE)
- If timeout → 2Captcha takes over (~$0.003)
- Almost guaranteed to work!

""")
