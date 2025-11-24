#!/usr/bin/env python3
"""
Local test script for display functionality.
Tests Xvfb setup and browser launch in visible mode.
"""

import sys
import os
import subprocess
import asyncio
import time
from pathlib import Path

# Add the automation directory to path
sys.path.insert(0, str(Path(__file__).parent / "automation" / "submission"))

def test_xvfb_availability():
    """Test if Xvfb is available."""
    print("=" * 80)
    print("TEST 1: Checking Xvfb Availability")
    print("=" * 80)
    
    # Check if Xvfb is installed
    xvfb_path = None
    for path in ['/usr/bin/Xvfb', '/usr/local/bin/Xvfb']:
        if os.path.exists(path):
            xvfb_path = path
            print(f"✅ Xvfb found at: {path}")
            break
    
    if not xvfb_path:
        try:
            result = subprocess.run(['which', 'Xvfb'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                xvfb_path = result.stdout.strip()
                print(f"✅ Xvfb found at: {xvfb_path}")
        except:
            pass
    
    if not xvfb_path:
        print("❌ Xvfb not found")
        print("   Install with: sudo apt-get install xvfb")
        return False
    
    # Check xvfb-run
    xvfb_run = None
    for path in ['/usr/bin/xvfb-run', '/usr/local/bin/xvfb-run']:
        if os.path.exists(path):
            xvfb_run = path
            print(f"✅ xvfb-run found at: {path}")
            break
    
    if not xvfb_run:
        try:
            result = subprocess.run(['which', 'xvfb-run'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                xvfb_run = result.stdout.strip()
                print(f"✅ xvfb-run found at: {xvfb_run}")
        except:
            print("⚠️  xvfb-run not found (optional)")
    
    print()
    return True

def test_xvfb_start():
    """Test starting Xvfb manually."""
    print("=" * 80)
    print("TEST 2: Starting Xvfb Virtual Display")
    print("=" * 80)
    
    # Find Xvfb
    xvfb_path = None
    for path in ['/usr/bin/Xvfb', '/usr/local/bin/Xvfb']:
        if os.path.exists(path):
            xvfb_path = path
            break
    
    if not xvfb_path:
        try:
            result = subprocess.run(['which', 'Xvfb'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                xvfb_path = result.stdout.strip()
        except:
            pass
    
    if not xvfb_path:
        print("❌ Xvfb not found - cannot test")
        return None, None
    
    # Try multiple display numbers (99-110)
    for display_num in range(99, 111):
        display = f":{display_num}"
        print(f"🔄 Attempting to start Xvfb on {display}...")
        
        # Check if lock file exists and try to clean it up
        lock_file = f"/tmp/.X{display_num}-lock"
        if os.path.exists(lock_file):
            print(f"   ⚠️  Lock file exists: {lock_file}")
            # Check if process is actually running
            try:
                # Try to read the PID from lock file
                with open(lock_file, 'r') as f:
                    lock_content = f.read()
                # Try to kill the process if it exists
                try:
                    import signal
                    pid = int(lock_content.strip().split()[0])
                    os.kill(pid, 0)  # Check if process exists
                    print(f"   ℹ️  Process {pid} is running - trying next display")
                    continue
                except (ValueError, ProcessLookupError, OSError):
                    # Process doesn't exist, remove lock file
                    print(f"   🗑️  Removing stale lock file...")
                    os.remove(lock_file)
            except:
                # Can't read lock file, try to remove it anyway
                try:
                    os.remove(lock_file)
                    print(f"   🗑️  Removed lock file")
                except:
                    pass
        
        try:
            process = subprocess.Popen(
                [xvfb_path, display, '-screen', '0', '1280x720x24', '-ac', '+extension', 'GLX'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid
            )
            
            # Wait a moment
            time.sleep(1)
            
            if process.poll() is None:  # Still running
                print(f"✅ Xvfb started successfully on {display}")
                print(f"   Process PID: {process.pid}")
                return process, display
            else:
                stderr = process.stderr.read().decode() if process.stderr else ""
                if "already active" in stderr or "already in use" in stderr:
                    print(f"   ⚠️  Display {display} already in use, trying next...")
                    continue
                else:
                    print(f"   ⚠️  Xvfb failed: {stderr[:100]}")
                    continue
        except Exception as e:
            print(f"   ⚠️  Error starting Xvfb on {display}: {str(e)[:50]}")
            continue
    
    print("❌ Could not start Xvfb on any display (tried 99-110)")
    return None, None

def test_display_environment(display):
    """Test setting DISPLAY environment variable."""
    print("=" * 80)
    print("TEST 3: Setting DISPLAY Environment Variable")
    print("=" * 80)
    
    if not display:
        print("❌ No display provided")
        return False
    
    # Set DISPLAY
    os.environ['DISPLAY'] = display
    print(f"✅ Set DISPLAY={display}")
    
    # Verify it's set
    current_display = os.environ.get('DISPLAY')
    if current_display == display:
        print(f"✅ Verified: DISPLAY is {current_display}")
        return True
    else:
        print(f"❌ DISPLAY mismatch: expected {display}, got {current_display}")
        return False

async def test_browser_launch():
    """Test launching browser with Playwright."""
    print("=" * 80)
    print("TEST 4: Launching Browser with Playwright")
    print("=" * 80)
    
    try:
        from playwright.async_api import async_playwright
        
        print("🔄 Starting Playwright...")
        playwright = await async_playwright().start()
        print("✅ Playwright started")
        
        # Check current DISPLAY
        current_display = os.environ.get('DISPLAY', 'NOT SET')
        print(f"   Current DISPLAY: {current_display}")
        
        if current_display == 'NOT SET':
            print("⚠️  WARNING: DISPLAY not set - browser may fail to launch")
        
        print("🔄 Launching Chromium in visible mode...")
        try:
            browser = await playwright.chromium.launch(
                headless=False,  # Visible mode
                timeout=30000,
                args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
            )
            print("✅ Browser launched successfully!")
            
            print("🔄 Creating page...")
            page = await browser.new_page()
            print("✅ Page created")
            
            print("🔄 Navigating to example.com...")
            await page.goto('https://example.com', timeout=10000)
            print("✅ Navigation successful")
            
            title = await page.title()
            print(f"✅ Page loaded: {title}")
            
            # Clean up
            await browser.close()
            await playwright.stop()
            print("✅ Browser closed")
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Browser launch failed: {error_msg[:200]}")
            
            if "Missing X server" in error_msg or "DISPLAY" in error_msg:
                print("   💡 This error indicates DISPLAY is not set or Xvfb is not running")
            
            try:
                await playwright.stop()
            except:
                pass
            
            return False
            
    except ImportError:
        print("❌ Playwright not installed")
        print("   Install with: pip install playwright && playwright install chromium")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

async def test_full_workflow():
    """Test the full workflow: Xvfb setup -> DISPLAY -> Browser."""
    print("=" * 80)
    print("TEST 5: Full Workflow Test")
    print("=" * 80)
    print()
    
    # Step 1: Start Xvfb
    xvfb_process, display = test_xvfb_start()
    if not xvfb_process:
        print("❌ Cannot continue - Xvfb failed to start")
        return False
    
    print()
    
    # Step 2: Set DISPLAY
    if not test_display_environment(display):
        print("❌ Cannot continue - DISPLAY not set")
        try:
            os.killpg(os.getpgid(xvfb_process.pid), 15)
        except:
            pass
        return False
    
    print()
    
    # Step 3: Launch browser
    browser_success = await test_browser_launch()
    
    print()
    
    # Cleanup
    print("🔄 Cleaning up Xvfb...")
    try:
        os.killpg(os.getpgid(xvfb_process.pid), 15)
        xvfb_process.wait(timeout=5)
        print("✅ Xvfb stopped")
    except:
        try:
            os.killpg(os.getpgid(xvfb_process.pid), 9)
        except:
            pass
    
    if 'DISPLAY' in os.environ:
        del os.environ['DISPLAY']
    
    print()
    
    if browser_success:
        print("=" * 80)
        print("✅ ALL TESTS PASSED - Display functionality is working!")
        print("=" * 80)
        return True
    else:
        print("=" * 80)
        print("❌ TESTS FAILED - Check the errors above")
        print("=" * 80)
        return False

async def main():
    """Run all tests."""
    print()
    print("=" * 80)
    print("  LOCAL DISPLAY FUNCTIONALITY TEST")
    print("=" * 80)
    print()
    
    # Test 1: Check availability
    if not test_xvfb_availability():
        print("\n❌ Xvfb not available - install it first")
        return 1
    
    print()
    
    # Test 2-5: Full workflow
    success = await test_full_workflow()
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

