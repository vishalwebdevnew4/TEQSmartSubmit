#!/usr/bin/env python3
"""
Run automation for multiple URLs using a single browser tab.

This script reuses the same browser tab, just navigating to different URLs.
The browser runs in the background (headless=False with virtual display).
"""

import asyncio
import json
import sys
from pathlib import Path

# Add automation directory to path
sys.path.insert(0, str(Path(__file__).parent))

from browser_manager import BrowserManager
from run_submission import run_submission


async def run_multiple_urls(urls: list, template_path: Path, headless: bool = False, use_virtual_display: bool = True):
    """
    Run automation for multiple URLs using a single browser tab.
    
    Args:
        urls: List of URLs to process
        template_path: Path to template JSON file
        headless: Whether to run in headless mode (False = visible but in background)
        use_virtual_display: Whether to use virtual display for background operation
    """
    # Load template
    template = json.loads(template_path.read_text())
    
    # Enable browser reuse in template
    template['reuse_browser'] = True
    template['headless'] = headless
    template['use_virtual_display'] = use_virtual_display
    
    # Save updated template
    updated_template_path = template_path.parent / f"{template_path.stem}_reuse.json"
    updated_template_path.write_text(json.dumps(template, indent=2))
    
    # Create browser manager
    browser_manager = BrowserManager(
        headless=headless,
        use_virtual_display=use_virtual_display
    )
    
    results = []
    
    try:
        # Start browser once
        print("=" * 70)
        print("Starting persistent browser (single tab mode)")
        print("=" * 70)
        await browser_manager.start()
        
        # Process each URL
        for i, url in enumerate(urls, 1):
            print(f"\n{'=' * 70}")
            print(f"Processing URL {i}/{len(urls)}: {url}")
            print(f"{'=' * 70}\n")
            
            try:
                result = await run_submission(
                    url=url,
                    template_path=updated_template_path,
                    browser_manager=browser_manager
                )
                results.append({
                    'url': url,
                    'result': result,
                    'success': result.get('status') == 'success'
                })
                print(f"\n✅ Completed: {url} - Status: {result.get('status')}")
            except Exception as e:
                error_msg = str(e)
                print(f"\n❌ Failed: {url} - Error: {error_msg[:200]}")
                results.append({
                    'url': url,
                    'result': {'status': 'error', 'message': error_msg},
                    'success': False
                })
            
            # Small delay between URLs
            if i < len(urls):
                print("\n⏳ Waiting 2 seconds before next URL...\n")
                await asyncio.sleep(2)
        
    finally:
        # Stop browser
        print("\n" + "=" * 70)
        print("Stopping browser")
        print("=" * 70)
        await browser_manager.stop()
    
    # Print summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    successful = sum(1 for r in results if r['success'])
    print(f"Total URLs: {len(urls)}")
    print(f"Successful: {successful}")
    print(f"Failed: {len(urls) - successful}")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run automation for multiple URLs using single browser tab")
    parser.add_argument("--urls", required=True, help="Comma-separated list of URLs or path to file with URLs (one per line)")
    parser.add_argument("--template", required=True, help="Path to template JSON file")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode (default: False = visible but in background)")
    parser.add_argument("--no-virtual-display", action="store_true", help="Don't use virtual display")
    
    args = parser.parse_args()
    
    # Parse URLs
    if Path(args.urls).exists():
        # Read from file
        urls = [line.strip() for line in Path(args.urls).read_text().splitlines() if line.strip()]
    else:
        # Parse from comma-separated string
        urls = [url.strip() for url in args.urls.split(',') if url.strip()]
    
    if not urls:
        print("❌ No URLs provided", file=sys.stderr)
        sys.exit(1)
    
    template_path = Path(args.template)
    if not template_path.exists():
        print(f"❌ Template file not found: {template_path}", file=sys.stderr)
        sys.exit(1)
    
    # Run
    results = asyncio.run(run_multiple_urls(
        urls=urls,
        template_path=template_path,
        headless=args.headless,
        use_virtual_display=not args.no_virtual_display
    ))
    
    # Exit with error code if any failed
    if any(not r['success'] for r in results):
        sys.exit(1)

