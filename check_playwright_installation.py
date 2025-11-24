#!/usr/bin/env python3
"""
Playwright Installation Diagnostic Script
Checks what's installed and what needs to be installed.
"""

import sys
import subprocess
import os
from pathlib import Path

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def print_section(text):
    print(f"\n📋 {text}")
    print("-" * 80)

def check_command(command, description):
    """Check if a command exists and is executable."""
    try:
        result = subprocess.run(
            ['which', command],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            path = result.stdout.strip()
            print(f"   ✅ {description}: {path}")
            return True, path
        else:
            print(f"   ❌ {description}: Not found")
            return False, None
    except Exception as e:
        print(f"   ⚠️  {description}: Error checking - {str(e)}")
        return False, None

def check_python_package(package_name):
    """Check if a Python package is installed."""
    try:
        __import__(package_name)
        # Try to get version
        try:
            import importlib.metadata
            version = importlib.metadata.version(package_name)
            print(f"   ✅ {package_name}: Installed (version {version})")
        except:
            try:
                import pkg_resources
                version = pkg_resources.get_distribution(package_name).version
                print(f"   ✅ {package_name}: Installed (version {version})")
            except:
                print(f"   ✅ {package_name}: Installed (version unknown)")
        return True
    except ImportError:
        print(f"   ❌ {package_name}: Not installed")
        return False
    except Exception as e:
        print(f"   ⚠️  {package_name}: Error checking - {str(e)}")
        return False

def check_playwright_browsers():
    """Check if Playwright browsers are installed."""
    browsers_installed = []
    browsers_missing = []
    
    browser_paths = {
        'chromium': [
            Path.home() / '.cache' / 'ms-playwright' / 'chromium-*',
            Path.home() / '.local' / 'share' / 'ms-playwright' / 'chromium-*',
        ],
        'firefox': [
            Path.home() / '.cache' / 'ms-playwright' / 'firefox-*',
            Path.home() / '.local' / 'share' / 'ms-playwright' / 'firefox-*',
        ],
        'webkit': [
            Path.home() / '.cache' / 'ms-playwright' / 'webkit-*',
            Path.home() / '.local' / 'share' / 'ms-playwright' / 'webkit-*',
        ],
    }
    
    try:
        from playwright.sync_api import sync_playwright
        p = sync_playwright().start()
        
        for browser_name in ['chromium', 'firefox', 'webkit']:
            try:
                browser_type = getattr(p, browser_name)
                executable_path = browser_type.executable_path
                if executable_path and Path(executable_path).exists():
                    print(f"   ✅ {browser_name}: Installed at {executable_path}")
                    browsers_installed.append(browser_name)
                else:
                    print(f"   ❌ {browser_name}: Not installed")
                    browsers_missing.append(browser_name)
            except Exception as e:
                print(f"   ❌ {browser_name}: Not installed ({str(e)[:50]})")
                browsers_missing.append(browser_name)
        
        p.stop()
    except ImportError:
        print("   ⚠️  Cannot check browsers - Playwright not installed")
        return [], ['chromium', 'firefox', 'webkit']
    except Exception as e:
        print(f"   ⚠️  Error checking browsers: {str(e)[:100]}")
        return [], ['chromium', 'firefox', 'webkit']
    
    return browsers_installed, browsers_missing

def check_system_dependencies():
    """Check if system dependencies are installed (Linux only)."""
    if sys.platform not in ['linux', 'linux2']:
        print("   ℹ️  System dependency check is for Linux only")
        return []
    
    dependencies = {
        'libnss3': ['libnss3'],
        'libatk': ['libatk1.0-0', 'libatk-bridge2.0-0'],
        'libcups': ['libcups2'],
        'libdrm': ['libdrm2'],
        'libxkbcommon': ['libxkbcommon0'],
        'libxcomposite': ['libxcomposite1'],
        'libxdamage': ['libxdamage1'],
        'libxfixes': ['libxfixes3'],
        'libxrandr': ['libxrandr2'],
        'libgbm': ['libgbm1'],
        'libasound': ['libasound2'],
    }
    
    missing = []
    
    # Try to detect package manager
    has_apt = check_command('apt', 'apt package manager')[0]
    has_yum = check_command('yum', 'yum package manager')[0]
    has_dpkg = check_command('dpkg', 'dpkg package manager')[0]
    has_rpm = check_command('rpm', 'rpm package manager')[0]
    
    if has_dpkg or has_apt:
        # Debian/Ubuntu
        print("   📦 Using apt/dpkg to check packages...")
        for dep_name, package_names in dependencies.items():
            found = False
            for pkg in package_names:
                try:
                    result = subprocess.run(
                        ['dpkg', '-l', pkg],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and pkg in result.stdout:
                        print(f"   ✅ {dep_name} ({pkg}): Installed")
                        found = True
                        break
                except:
                    pass
            
            if not found:
                print(f"   ❌ {dep_name}: Not installed (need: {', '.join(package_names)})")
                missing.append(dep_name)
    
    elif has_rpm or has_yum:
        # CentOS/RHEL
        print("   📦 Using rpm/yum to check packages...")
        for dep_name, package_names in dependencies.items():
            found = False
            for pkg in package_names:
                try:
                    result = subprocess.run(
                        ['rpm', '-q', pkg],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print(f"   ✅ {dep_name} ({pkg}): Installed")
                        found = True
                        break
                except:
                    pass
            
            if not found:
                print(f"   ❌ {dep_name}: Not installed (need: {', '.join(package_names)})")
                missing.append(dep_name)
    else:
        print("   ⚠️  Could not detect package manager - skipping dependency check")
        print("   ℹ️  Please manually check if system dependencies are installed")
    
    return missing

def get_installation_commands(missing_browsers, missing_deps, playwright_installed):
    """Generate installation commands based on what's missing."""
    commands = []
    
    print_section("📝 Installation Commands")
    
    if not playwright_installed:
        print("\n1️⃣  Install Playwright Python package:")
        print("   pip install playwright")
        print("   # OR")
        print("   pip3 install playwright")
        commands.append("pip install playwright")
    
    if missing_browsers:
        print(f"\n2️⃣  Install Playwright browsers ({', '.join(missing_browsers)}):")
        if 'chromium' in missing_browsers:
            print("   playwright install chromium")
            commands.append("playwright install chromium")
        else:
            print("   playwright install")
            commands.append("playwright install")
        print("   # OR if using system Python:")
        print("   python3 -m playwright install chromium")
    
    if missing_deps and sys.platform in ['linux', 'linux2']:
        print(f"\n3️⃣  Install system dependencies ({len(missing_deps)} missing):")
        
        # Detect package manager
        has_apt = subprocess.run(['which', 'apt-get'], capture_output=True).returncode == 0
        has_yum = subprocess.run(['which', 'yum'], capture_output=True).returncode == 0
        
        if has_apt:
            print("   # Ubuntu/Debian:")
            deps_list = [
                'libnss3', 'libatk1.0-0', 'libatk-bridge2.0-0',
                'libcups2', 'libdrm2', 'libxkbcommon0',
                'libxcomposite1', 'libxdamage1', 'libxfixes3',
                'libxrandr2', 'libgbm1', 'libasound2'
            ]
            cmd = f"sudo apt-get update && sudo apt-get install -y {' '.join(deps_list)}"
            print(f"   {cmd}")
            commands.append(cmd)
        
        elif has_yum:
            print("   # CentOS/RHEL:")
            deps_list = [
                'nss', 'atk', 'at-spi2-atk', 'cups-libs',
                'libdrm', 'libxkbcommon', 'libXcomposite',
                'libXdamage', 'libXfixes', 'libXrandr',
                'mesa-libgbm', 'alsa-lib'
            ]
            cmd = f"sudo yum install -y {' '.join(deps_list)}"
            print(f"   {cmd}")
            commands.append(cmd)
    
    if not commands:
        print("\n   ✅ Everything is installed! No action needed.")
    
    return commands

def main():
    print_header("Playwright Installation Diagnostic Tool")
    print("\nThis script checks what's installed and what needs to be installed.")
    
    # Check Python version
    print_section("Python Environment")
    print(f"   Python version: {sys.version}")
    print(f"   Python executable: {sys.executable}")
    
    # Check commands
    print_section("System Commands")
    check_command('python3', 'Python 3')
    check_command('pip', 'pip')
    check_command('pip3', 'pip3')
    check_command('playwright', 'Playwright CLI')
    
    # Check Python packages
    print_section("Python Packages")
    playwright_installed = check_python_package('playwright')
    
    # Check browsers
    print_section("Playwright Browsers")
    browsers_installed, browsers_missing = check_playwright_browsers()
    
    # Check system dependencies (Linux only)
    print_section("System Dependencies (Linux)")
    missing_deps = check_system_dependencies()
    
    # Summary
    print_header("Summary")
    
    all_good = True
    
    if not playwright_installed:
        print("❌ Playwright Python package: NOT INSTALLED")
        all_good = False
    else:
        print("✅ Playwright Python package: INSTALLED")
    
    if browsers_missing:
        print(f"❌ Playwright browsers: MISSING ({', '.join(browsers_missing)})")
        all_good = False
    else:
        print(f"✅ Playwright browsers: INSTALLED ({', '.join(browsers_installed)})")
    
    if missing_deps:
        print(f"⚠️  System dependencies: MISSING ({len(missing_deps)} packages)")
        all_good = False
    else:
        print("✅ System dependencies: INSTALLED")
    
    # Installation commands
    if not all_good:
        get_installation_commands(browsers_missing, missing_deps, playwright_installed)
    else:
        print("\n✅ All checks passed! Playwright is ready to use.")
    
    print("\n" + "=" * 80)
    print("  Diagnostic complete")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()

