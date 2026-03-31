#!/usr/bin/env python3
"""
Direct test - run automation script directly without subprocess
"""

import asyncio
import json
import tempfile
from pathlib import Path

# Import the automation module directly
import sys
sys.path.insert(0, '/var/www/html/TEQSmartSubmit/automation')
sys.path.insert(0, '/var/www/html/TEQSmartSubmit')

async def test_direct():
    from automation.run_submission import run_submission
    
    template = {
        "fields": [
            {
                "selector": 'input[name="name"]',
                "value": "Direct Test"
            },
            {
                "selector": 'input[name="email"]',
                "value": "direct@example.com"
            },
            {
                "selector": 'input[name="phone"]',
                "value": "+31600000002"
            },
            {
                "selector": 'textarea[name="comment"]',
                "value": "Direct automation test"
            }
        ],
        "submit_selector": 'button:has-text("Bericht verzenden")',
        "post_submit_wait_ms": 20000,
        "use_local_captcha_solver": False,
        "headless": True
    }
    
    # Write template
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(template, f)
        template_file = Path(f.name)
    
    try:
        print("Starting submission...")
        result = await asyncio.wait_for(
            run_submission("https://interiordesign.xcelanceweb.com/", template_file),
            timeout=90
        )
        print("\nResult:")
        print(json.dumps(result, indent=2))
    except asyncio.TimeoutError:
        print("\n❌ TIMEOUT after 90 seconds!")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        template_file.unlink(missing_ok=True)

if __name__ == '__main__':
    asyncio.run(test_direct())
