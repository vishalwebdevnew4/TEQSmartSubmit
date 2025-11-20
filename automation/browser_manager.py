#!/usr/bin/env python3
"""
Browser Manager for Reusing Browser Tab Across Multiple URLs

This module manages a persistent browser instance that can be reused
for multiple automation runs, just navigating to different URLs in the same tab.
"""

import asyncio
import os
import sys
from typing import Optional
from pathlib import Path

try:
    from playwright.async_api import Browser, BrowserContext, Page, async_playwright
except ImportError:
    Browser = None
    BrowserContext = None
    Page = None
    async_playwright = None


class BrowserManager:
    """Manages a persistent browser instance for reuse across multiple URLs."""
    
    def __init__(self, headless: bool = False, use_virtual_display: bool = False):
        """
        Initialize browser manager.
        
        Args:
            headless: Whether to run browser in headless mode
            use_virtual_display: Whether to use virtual display (for background operation)
        """
        self.headless = headless
        self.use_virtual_display = use_virtual_display
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.vdisplay = None
        
        # Import virtual display if needed
        if use_virtual_display:
            try:
                from virtual_display import VirtualDisplay, ensure_virtual_display
                self.VirtualDisplay = VirtualDisplay
                self.ensure_virtual_display = ensure_virtual_display
            except ImportError:
                self.VirtualDisplay = None
                self.ensure_virtual_display = None
    
    async def start(self):
        """Start the browser and create a persistent tab."""
        if async_playwright is None:
            raise ImportError("Playwright is not installed")
        
        # Start virtual display if needed
        if self.use_virtual_display and self.VirtualDisplay is not None:
            print("🖥️  Starting virtual display for background browser...", file=sys.stderr)
            self.vdisplay = self.ensure_virtual_display(display_num=99, force=True)
            if self.vdisplay and self.vdisplay.is_running:
                # For non-headless mode, set DISPLAY so browser renders on virtual display
                if not self.headless:
                    self.vdisplay.set_display_env()
                    print(f"   ✅ Virtual display active (DISPLAY={os.environ.get('DISPLAY')})", file=sys.stderr)
                else:
                    print("   ✅ Virtual display started (not setting DISPLAY for headless)", file=sys.stderr)
            else:
                print("   ⚠️  Virtual display not available", file=sys.stderr)
        
        # Start Playwright
        try:
            self.playwright = await async_playwright().__aenter__()
        except Exception as e:
            error_str = str(e)
            if "has been closed" in error_str or "Target" in error_str:
                print(f"   ⚠️  Playwright instance was closed, creating new one...", file=sys.stderr)
                # Try to create a new playwright instance
                self.playwright = await async_playwright().__aenter__()
            else:
                raise
        
        # Launch browser
        print(f"🚀 Launching browser (headless={self.headless})...", file=sys.stderr)
        try:
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                timeout=180000,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--window-size=1920,1080',
                    '--start-maximized',
                ] if not self.headless else []
            )
            print("   ✅ Browser launched", file=sys.stderr)
        except Exception as e:
            error_str = str(e)
            if "has been closed" in error_str or "Target" in error_str:
                print(f"   ⚠️  Browser launch failed - Playwright instance was closed: {error_str[:100]}", file=sys.stderr)
                # Try to recreate playwright instance and retry
                try:
                    if self.playwright:
                        await self.playwright.__aexit__(None, None, None)
                except:
                    pass
                self.playwright = await async_playwright().__aenter__()
                self.browser = await self.playwright.chromium.launch(
                    headless=self.headless,
                    timeout=180000,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--window-size=1920,1080',
                        '--start-maximized',
                    ] if not self.headless else []
                )
                print("   ✅ Browser launched (after retry)", file=sys.stderr)
            else:
                raise
        
        # Create context
        print("   📦 Creating browser context...", file=sys.stderr)
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            storage_state=None,
        )
        self.context.set_default_timeout(180000)
        print("   ✅ Context created", file=sys.stderr)
        
        # Add stealth scripts
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.chrome = { runtime: {} };
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            if (navigator.getBattery) {
                navigator.getBattery = () => Promise.resolve({ charging: true, chargingTime: 0, dischargingTime: Infinity, level: 1 });
            }
        """)
        print("   ✅ Stealth scripts added", file=sys.stderr)
        
        # Create page (single tab that will be reused)
        print("   📄 Creating persistent page (will be reused for all URLs)...", file=sys.stderr)
        self.page = await self.context.new_page()
        self.page.set_default_timeout(180000)
        print("   ✅ Persistent page created - ready to navigate to URLs", file=sys.stderr)
    
    async def navigate_to(self, url: str, wait_until: str = "domcontentloaded", timeout: int = 30000):
        """
        Navigate to a new URL in the existing tab.
        
        Args:
            url: URL to navigate to
            wait_until: When to consider navigation finished
            timeout: Navigation timeout in milliseconds
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        
        # Verify page is still valid before navigating
        try:
            _ = self.page.url
        except Exception as e:
            error_str = str(e)
            if "has been closed" in error_str or "Target" in error_str:
                raise RuntimeError(f"Browser page was closed: {error_str}")
            raise
        
        print(f"   🔄 Navigating to: {url}", file=sys.stderr)
        try:
            await self.page.goto(url, wait_until=wait_until, timeout=timeout)
            print("   ✅ Navigation complete", file=sys.stderr)
        except Exception as e:
            error_str = str(e)
            if "has been closed" in error_str or "Target" in error_str:
                print(f"   ⚠️  Browser closed during navigation: {error_str[:100]}", file=sys.stderr)
                raise RuntimeError(f"Browser was closed during navigation: {error_str}")
            print(f"   ⚠️  Navigation error: {str(e)[:100]}", file=sys.stderr)
            raise
    
    async def stop(self):
        """Stop the browser and cleanup."""
        print("🔒 Closing browser...", file=sys.stderr)
        
        try:
            if self.page:
                await self.page.close()
        except Exception as e:
            print(f"   ⚠️  Error closing page: {str(e)[:50]}", file=sys.stderr)
        
        try:
            if self.context:
                await self.context.close()
        except Exception as e:
            print(f"   ⚠️  Error closing context: {str(e)[:50]}", file=sys.stderr)
        
        try:
            if self.browser:
                await self.browser.close()
        except Exception as e:
            print(f"   ⚠️  Error closing browser: {str(e)[:50]}", file=sys.stderr)
        
        try:
            if self.playwright:
                await self.playwright.__aexit__(None, None, None)
        except Exception as e:
            print(f"   ⚠️  Error closing playwright: {str(e)[:50]}", file=sys.stderr)
        
        # Clean up virtual display
        if self.vdisplay and self.vdisplay.is_running:
            print("🖥️  Cleaning up virtual display...", file=sys.stderr)
            self.vdisplay.restore_display_env()
            self.vdisplay.stop()
        
        print("   ✅ Browser closed", file=sys.stderr)
    
    def get_page(self) -> Optional[Page]:
        """Get the persistent page."""
        return self.page
    
    def get_context(self) -> Optional[BrowserContext]:
        """Get the browser context."""
        return self.context
    
    def get_browser(self) -> Optional[Browser]:
        """Get the browser instance."""
        return self.browser

