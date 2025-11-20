#!/usr/bin/env python3
"""
Virtual Display Manager for Headless Browser Automation

This module manages Xvfb (X Virtual Framebuffer) to provide a virtual display
for browsers when running in headless environments. This allows browsers to
render to a virtual display instead of requiring a physical monitor.

Usage:
    from virtual_display import VirtualDisplay
    
    with VirtualDisplay() as display:
        # Browser will use DISPLAY=:99
        # Run your automation here
        pass
    # Display is automatically cleaned up
"""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional


class VirtualDisplay:
    """Manages an Xvfb virtual display for headless browser automation."""
    
    def __init__(
        self,
        display_num: int = 99,
        width: int = 1920,
        height: int = 1080,
        depth: int = 24,
        auto_start: bool = True
    ):
        """
        Initialize virtual display manager.
        
        Args:
            display_num: Display number (e.g., 99 for :99)
            width: Screen width in pixels
            height: Screen height in pixels
            depth: Color depth (bits per pixel)
            auto_start: Automatically start display on context enter
        """
        self.display_num = display_num
        self.display_name = f":{display_num}"
        self.width = width
        self.height = height
        self.depth = depth
        self.auto_start = auto_start
        self.process: Optional[subprocess.Popen] = None
        self.original_display: Optional[str] = None
        self.is_running = False
        
    def _check_xvfb_available(self) -> bool:
        """Check if Xvfb is installed and available."""
        try:
            result = subprocess.run(
                ["which", "Xvfb"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _is_display_in_use(self) -> bool:
        """Check if the display number is already in use."""
        try:
            # Try to connect to the display
            result = subprocess.run(
                ["xdpyinfo", "-display", self.display_name],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            # xdpyinfo not available or timeout - assume not in use
            return False
    
    def start(self) -> bool:
        """
        Start the virtual display.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.is_running:
            print(f"   ℹ️  Virtual display {self.display_name} is already running", file=sys.stderr)
            return True
        
        if not self._check_xvfb_available():
            print(f"   ⚠️  Xvfb not found. Install with: sudo apt-get install xvfb (or without sudo: see setup guide)", file=sys.stderr)
            return False
        
        # Check if display is already in use
        if self._is_display_in_use():
            print(f"   ℹ️  Display {self.display_name} is already in use, reusing it", file=sys.stderr)
            self.is_running = True
            return True
        
        try:
            # Start Xvfb with the specified display number
            cmd = [
                "Xvfb",
                self.display_name,
                "-screen", "0", f"{self.width}x{self.height}x{self.depth}",
                "-ac",  # Disable access control
                "-nolisten", "tcp",  # Disable TCP connections for security
                "-dpi", "96",  # Set DPI
                "+extension", "RANDR",  # Enable RANDR extension for resolution changes
            ]
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ.copy()
            )
            
            # Wait for Xvfb to start and become ready
            # Try multiple times to ensure display is accessible
            max_attempts = 10
            for attempt in range(max_attempts):
                time.sleep(0.5)
                
                # Check if process is still running
                if self.process.poll() is not None:
                    # Process exited, check for errors
                    stdout, stderr = self.process.communicate()
                    error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "Unknown error"
                    print(f"   ❌ Failed to start Xvfb: {error_msg}", file=sys.stderr)
                    return False
                
                # Verify display is accessible
                if self._is_display_in_use():
                    # Display is ready!
                    break
            else:
                # If we get here, display never became accessible
                print(f"   ❌ Xvfb started but display {self.display_name} is not accessible after {max_attempts} attempts", file=sys.stderr)
                self.stop()
                return False
            
            self.is_running = True
            print(f"   ✅ Virtual display {self.display_name} started ({self.width}x{self.height}x{self.depth})", file=sys.stderr)
            return True
            
        except Exception as e:
            print(f"   ❌ Error starting virtual display: {e}", file=sys.stderr)
            if self.process:
                self.stop()
            return False
    
    def stop(self):
        """Stop the virtual display."""
        if not self.is_running:
            return
        
        if self.process:
            try:
                self.process.terminate()
                # Wait up to 2 seconds for graceful shutdown
                try:
                    self.process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    # Force kill if it doesn't terminate
                    self.process.kill()
                    self.process.wait()
                
                self.process = None
                print(f"   ✅ Virtual display {self.display_name} stopped", file=sys.stderr)
            except Exception as e:
                print(f"   ⚠️  Error stopping virtual display: {e}", file=sys.stderr)
        
        self.is_running = False
    
    def set_display_env(self):
        """Set DISPLAY environment variable to use this virtual display."""
        self.original_display = os.environ.get("DISPLAY")
        os.environ["DISPLAY"] = self.display_name
        print(f"   ℹ️  Set DISPLAY={self.display_name}", file=sys.stderr)
    
    def restore_display_env(self):
        """Restore original DISPLAY environment variable."""
        if self.original_display is not None:
            os.environ["DISPLAY"] = self.original_display
        elif "DISPLAY" in os.environ:
            del os.environ["DISPLAY"]
    
    def __enter__(self):
        """Context manager entry."""
        if self.auto_start:
            if self.start():
                self.set_display_env()
            else:
                # If we can't start virtual display, continue anyway
                # The browser will use headless mode
                pass
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup."""
        self.restore_display_env()
        if self.auto_start:
            self.stop()
    
    def __del__(self):
        """Destructor - ensure cleanup."""
        # Don't automatically stop in __del__ - let explicit cleanup handle it
        # This prevents premature stopping when object is garbage collected
        pass


def ensure_virtual_display(display_num: int = 99, force: bool = False) -> Optional[VirtualDisplay]:
    """
    Ensure a virtual display is available, starting one if needed.
    
    Args:
        display_num: Display number to use
        force: If True, start virtual display even if another display is available
        
    Returns:
        VirtualDisplay instance if started, None if not needed or failed
    """
    # Check if the target virtual display is already running
    target_display = f":{display_num}"
    try:
        result = subprocess.run(
            ["xdpyinfo", "-display", target_display],
            capture_output=True,
            timeout=2
        )
        if result.returncode == 0:
            # Target virtual display is already running, reuse it
            vdisplay = VirtualDisplay(display_num=display_num, auto_start=False)
            vdisplay.is_running = True  # Mark as running since it's already active
            vdisplay.set_display_env()
            return vdisplay
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # If force is False, check if we already have a working display
    if not force:
        current_display = os.environ.get("DISPLAY")
        if current_display and current_display != "" and current_display != target_display:
            # Check if current display is accessible
            try:
                result = subprocess.run(
                    ["xdpyinfo", "-display", current_display],
                    capture_output=True,
                    timeout=2
                )
                if result.returncode == 0:
                    # Current display is working, don't need virtual display
                    return None
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
    
    # Try to start virtual display
    vdisplay = VirtualDisplay(display_num=display_num, auto_start=False)
    if vdisplay.start():
        vdisplay.set_display_env()
        return vdisplay
    
    return None


if __name__ == "__main__":
    # Test virtual display
    print("Testing Virtual Display Manager...")
    
    with VirtualDisplay() as display:
        if display.is_running:
            print(f"✅ Virtual display is running on {display.display_name}")
            print(f"   DISPLAY={os.environ.get('DISPLAY')}")
            
            # Test if we can use the display
            try:
                result = subprocess.run(
                    ["xdpyinfo", "-display", display.display_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    print("✅ Display is accessible")
                else:
                    print("❌ Display is not accessible")
            except Exception as e:
                print(f"⚠️  Could not test display: {e}")
        else:
            print("❌ Failed to start virtual display")
            print("   Install Xvfb: sudo apt-get install xvfb")
    
    print("Test complete.")

