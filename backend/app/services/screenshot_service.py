#!/usr/bin/env python3
"""
Screenshot Service - Takes screenshots of websites using Playwright.
"""

import json
import sys
import os
import argparse
import asyncio
import time
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


async def take_screenshot(
    url: str,
    output_path: Optional[str] = None,
    width: int = 1920,
    height: int = 1080,
    full_page: bool = True,
) -> dict:
    """
    Take a screenshot of a webpage.
    
    Returns:
        Dict with screenshot path and metadata
    """
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={"width": width, "height": height})
            
            # Navigate to URL
            await page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Wait a bit for any animations
            await page.wait_for_timeout(2000)
            
            # Generate output path if not provided
            if not output_path:
                output_dir = Path("/tmp/screenshots")
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = str(output_dir / f"screenshot_{int(time.time())}.png")
            
            # Take screenshot
            await page.screenshot(path=output_path, full_page=full_page)
            
            await browser.close()
            
            return {
                "success": True,
                "screenshot_path": output_path,
                "url": url,
                "width": width,
                "height": height,
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "url": url,
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Take screenshot of a website")
    parser.add_argument("--url", required=True, help="URL to screenshot")
    parser.add_argument("--output", help="Output file path")
    parser.add_argument("--width", type=int, default=1920, help="Viewport width")
    parser.add_argument("--height", type=int, default=1080, help="Viewport height")
    parser.add_argument("--full-page", action="store_true", help="Capture full page")
    
    args = parser.parse_args()
    
    try:
        result = asyncio.run(
            take_screenshot(
                args.url,
                args.output,
                args.width,
                args.height,
                args.full_page,
            )
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

