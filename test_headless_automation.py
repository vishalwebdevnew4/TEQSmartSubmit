#!/usr/bin/env python3
"""
Simple test with headless mode enabled to avoid browser window issues
"""

import subprocess
import json
import tempfile
from pathlib import Path

template = {
    "url": "https://interiordesign.xcelanceweb.com/",
    "fields": [
        {
            "selector": 'input[name="name"]',
            "value": "Headless Test"
        },
        {
            "selector": 'input[name="email"]',
            "value": "headless@example.com"
        },
        {
            "selector": 'input[name="phone"]',
            "value": "+31600000001"
        },
        {
            "selector": 'textarea[name="comment"]',
            "value": "Running in headless mode"
        }
    ],
    "submit_selector": 'button:has-text("Bericht verzenden")',
    "post_submit_wait_ms": 20000,
    "use_local_captcha_solver": False,  # DISABLE local solver to see if that's where hang is
    "headless": True,
    "skip_captcha": True  # Also skip CAPTCHA entirely for now
}

print("\n" + "="*80)
print("HEADLESS AUTOMATION TEST")
print("="*80)

# Write template to temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(template, f)
    template_file = f.name

try:
    result = subprocess.run(
        [
            'python3',
            'automation/run_submission.py',
            '--url', template['url'],
            '--template', template_file
        ],
        cwd='/var/www/html/TEQSmartSubmit',
        capture_output=True,
        text=True,
        timeout=200  # Increased to 200s
    )
    
    print("\n📋 STDERR Output (debug info):")
    print("="*80)
    print(result.stderr[-2000:] if len(result.stderr) > 2000 else result.stderr)
    
    print("\n📋 STDOUT Output (result JSON):")
    print("="*80)
    print(result.stdout)
    
    if result.returncode == 0:
        print("\n✅ Script succeeded!")
    else:
        print(f"\n❌ Script failed with code: {result.returncode}")
    
finally:
    Path(template_file).unlink(missing_ok=True)
