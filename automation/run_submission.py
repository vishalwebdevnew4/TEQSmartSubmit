#!/usr/bin/env python3
"""
Lightweight Playwright automation helper.

This script is designed to be orchestrated by the Next.js API route. It:
  * Loads a JSON template describing selectors and values to fill.
  * Navigates to the target URL.
  * Attempts to fill and submit the form.
  * Prints a JSON result to stdout so the caller can parse it.

Template structure example:
{
  "fields": [
    { "selector": "input[name='name']", "value": "John Doe" },
    { "selector": "#email", "value": "john@example.com" }
  ],
  "submit_selector": "button[type='submit']",
  "post_submit_wait_ms": 4000,
  "captcha": false
}
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


async def solve_captcha(_: Any) -> Dict[str, str]:
    """Placeholder captcha handler – extend with real solver if needed."""
    return {"status": "skipped"}


async def run_submission(url: str, template_path: Path) -> Dict[str, Any]:
    from playwright.async_api import async_playwright  # imported lazily for performance

    template: Dict[str, Any] = json.loads(template_path.read_text())
    fields: List[Dict[str, str]] = template.get("fields", [])
    submit_selector: str | None = template.get("submit_selector")
    if not submit_selector:
        raise ValueError("Template missing 'submit_selector'")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto(url, wait_until(template.get("wait_until", "networkidle")))

        for field in fields:
            selector = field.get("selector")
            value = field.get("value", "")
            if not selector:
                continue
            await page.fill(selector, value)

        if template.get("captcha"):
            captcha_result = await solve_captcha(page)
            if captcha_result.get("status") != "ok":
                raise RuntimeError("Captcha could not be solved automatically")

        await page.click(submit_selector)
        await page.wait_for_timeout(template.get("post_submit_wait_ms", 3000))

        result = {
            "status": "success",
            "url": url,
            "message": template.get("success_message", "Submission completed"),
        }

        await context.close()
        await browser.close()
        return result


async def main_async(args: argparse.Namespace) -> int:
    template_path = Path(args.template).resolve()
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    result = await run_submission(args.url, template_path)
    print(json.dumps(result))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Automate form submission via Playwright.")
    parser.add_argument("--url", required=True, help="Target form URL.")
    parser.add_argument(
        "--template",
        required=True,
        help="Path to JSON template describing form selectors and values.",
    )
    args = parser.parse_args()

    try:
        return asyncio.run(main_async(args))
    except Exception as exc:  # pragma: no cover - surfaced to caller
        error_payload = {"status": "error", "message": str(exc)}
        print(json.dumps(error_payload))
        return 1


if __name__ == "__main__":
    sys.exit(main())


