#!/usr/bin/env python3
"""
Test the complete automation using run_submission.py
"""

import subprocess
import json
import sys
import tempfile
from pathlib import Path

template = {
    "url": "https://interiordesign.xcelanceweb.com/",
    "fields": [
        {
            "selector": 'input[name="name"]',
            "value": "Full Automation Test"
        },
        {
            "selector": 'input[name="email"]',
            "value": "fulltest@example.com"
        },
        {
            "selector": 'input[name="phone"]',
            "value": "+31687654321"
        },
        {
            "selector": 'textarea[name="comment"]',
            "value": "Testing complete automation workflow with CAPTCHA solving"
        }
    ],
    "submit_selector": 'button:has-text("Bericht verzenden")',
    "post_submit_wait_ms": 20000,
    "use_local_captcha_solver": True,
    "captcha_service": "auto",
    "headless": False
}

print("\n" + "="*80)
print("TESTING COMPLETE AUTOMATION WITH run_submission.py")
print("="*80)

print(f"\n📋 Template:")
print(f"  URL: {template['url']}")
print(f"  Fields: {len(template['fields'])}")
print(f"  Use Local Solver: {template['use_local_captcha_solver']}")
print(f"  Headless: {template['headless']}")

# Write template to temp file
with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
    json.dump(template, f)
    template_file = f.name

print(f"\n📄 Template file: {template_file}")

# Call run_submission.py
print(f"\n🚀 Running automation script...")
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
        timeout=180
    )
    
    print("\n" + "="*80)
    print("STDOUT:")
    print("="*80)
    print(result.stdout)
    
    if result.stderr:
        print("\n" + "="*80)
        print("STDERR:")
        print("="*80)
        print(result.stderr)
    
    print("\n" + "="*80)
    print("RESULT:")
    print("="*80)
    print(f"Return code: {result.returncode}")
    
    if result.returncode == 0:
        print("✅ Automation script succeeded!")
        try:
            output = json.loads(result.stdout)
            print(f"Output: {json.dumps(output, indent=2)}")
        except:
            pass
    else:
        print("❌ Automation script failed!")
    
    # Cleanup
    Path(template_file).unlink(missing_ok=True)
        
except subprocess.TimeoutExpired:
    print("⏰ Script timeout (180s exceeded)")
    Path(template_file).unlink(missing_ok=True)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    Path(template_file).unlink(missing_ok=True)
