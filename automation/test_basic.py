#!/usr/bin/env python3
"""Test basic automation functionality."""

import asyncio
import sys
from pathlib import Path

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from run_submission import run_submission


async def test_basic():
    """Test basic automation with a simple URL."""
    print("=" * 70)
    print("Testing Basic Automation")
    print("=" * 70)
    print()
    
    # Simple test URL
    test_url = "https://www.example.com"
    
    # Create a simple template
    template_path = Path(__file__).parent / "test_basic_template.json"
    template_content = {
        "fields": [],
        "use_auto_detect": False,
        "headless": True,
        "use_local_captcha_solver": False,
        "captcha": False
    }
    
    # Write template
    import json
    with open(template_path, 'w') as f:
        json.dump(template_content, f, indent=2)
    
    print(f"Testing URL: {test_url}")
    print(f"Template: {template_path}")
    print()
    
    try:
        result = await run_submission(
            url=test_url,
            template_path=template_path
        )
        
        status = result.get('status', 'unknown')
        print()
        print("=" * 70)
        print(f"✅ Test completed - Status: {status}")
        print("=" * 70)
        print()
        print("Result:", json.dumps(result, indent=2))
        return 0
        
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ Test failed: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(test_basic())
    sys.exit(exit_code)

