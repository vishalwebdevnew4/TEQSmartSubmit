#!/usr/bin/env python3
"""
Open a target page and fill the detected contact form without submitting it.

Usage:
  python3 automation/test_fill_only.py --url https://www.teqtop.com/contact --template automation/auto_detect_template.json
"""

import argparse
import asyncio
import importlib.util
import json
import sys
from pathlib import Path

AUTOMATION_DIR = Path(__file__).parent
sys.path.insert(0, str(AUTOMATION_DIR))

form_discovery_path = AUTOMATION_DIR / "submission" / "form_discovery.py"
spec = importlib.util.spec_from_file_location("fill_only_form_discovery", form_discovery_path)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load form_discovery module from {form_discovery_path}")

form_discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(form_discovery)

UltimatePlaywrightManager = form_discovery.UltimatePlaywrightManager
handle_banners_and_popups = form_discovery.handle_banners_and_popups
ultra_safe_log_print = form_discovery.ultra_safe_log_print
ultra_safe_template_load = form_discovery.ultra_safe_template_load
ultra_simple_form_fill = form_discovery.ultra_simple_form_fill


async def main() -> int:
    parser = argparse.ArgumentParser(description="Fill a form without submitting it.")
    parser.add_argument("--url", required=True, help="Target page URL.")
    parser.add_argument(
        "--template",
        default=str(AUTOMATION_DIR / "auto_detect_template.json"),
        help="Path to template JSON.",
    )
    parser.add_argument(
        "--wait-after-fill",
        type=float,
        default=10.0,
        help="Seconds to keep the browser open after fill for inspection.",
    )
    args = parser.parse_args()

    template_path = Path(args.template).resolve()
    if not template_path.exists():
      print(json.dumps({"status": "error", "message": f"Template not found: {template_path}"}))
      return 1

    template = await ultra_safe_template_load(template_path)
    manager = UltimatePlaywrightManager(headless=False)

    try:
        ultra_safe_log_print("=" * 80)
        ultra_safe_log_print("🧪 FILL-ONLY TEST START")
        ultra_safe_log_print("=" * 80)
        ultra_safe_log_print(f"URL: {args.url}")
        ultra_safe_log_print(f"Template: {template_path}")

        started = await manager.start()
        if not started or not manager.page:
            print(json.dumps({"status": "error", "message": "Failed to start browser"}))
            return 1

        ultra_safe_log_print("🌐 Navigating to page...")
        navigated = await manager.navigate(args.url)
        if not navigated:
            print(json.dumps({"status": "error", "message": f"Failed to navigate to {args.url}"}))
            return 1

        await asyncio.sleep(2)

        ultra_safe_log_print("🚫 Handling banners and popups...")
        banners_closed = await handle_banners_and_popups(manager.page)
        ultra_safe_log_print(f"Closed banners/popups: {banners_closed}")

        ultra_safe_log_print("📋 Raising forms above overlays...")
        forms_updated = await manager.page.evaluate(
            """
            () => {
                const forms = document.querySelectorAll('form');
                let updated = 0;
                forms.forEach(form => {
                    form.style.position = 'relative';
                    form.style.zIndex = '999999';
                    form.style.backgroundColor = form.style.backgroundColor || 'transparent';
                    updated++;
                });
                return updated;
            }
            """
        )
        ultra_safe_log_print(f"Forms updated: {forms_updated}")

        ultra_safe_log_print("✍️ Filling form only...")
        fill_result = await ultra_simple_form_fill(manager.page, template)
        ultra_safe_log_print(f"Fill result: {fill_result}")

        field_snapshot = await manager.page.evaluate(
            """
            () => {
                const form = document.querySelector('form');
                if (!form) return { found: false, fields: [] };

                const fields = Array.from(form.querySelectorAll('input, textarea, select'))
                    .filter(field => field.type !== 'hidden' && field.type !== 'submit' && field.type !== 'button')
                    .map(field => ({
                        tag: field.tagName.toLowerCase(),
                        name: field.name || field.id || 'unnamed',
                        type: field.type || field.tagName.toLowerCase(),
                        value: field.type === 'checkbox' || field.type === 'radio'
                            ? String(field.checked)
                            : (field.value || ''),
                        visible: field.offsetParent !== null,
                        required: !!field.required,
                    }));

                return { found: true, fields };
            }
            """
        )

        result = {
            "status": "ok",
            "url": args.url,
            "template": str(template_path),
            "banners_closed": banners_closed,
            "forms_updated": forms_updated,
            "fill_result": fill_result,
            "field_snapshot": field_snapshot,
        }

        print(json.dumps(result, indent=2))

        if args.wait_after_fill > 0:
            ultra_safe_log_print(f"⏳ Waiting {args.wait_after_fill} seconds for visual inspection...")
            await asyncio.sleep(args.wait_after_fill)

        return 0
    finally:
        await manager.cleanup()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
