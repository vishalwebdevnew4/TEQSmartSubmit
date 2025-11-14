#!/usr/bin/env python3
"""
Verify Python installation on remote server.
"""

import pexpect
import sys

HOST = "teqsmartsubmit.xcelanceweb.com"
PORT = "3129"
USER = "teqsmartsftpuser"
PASSWORD = "XFho65rfr@uj()7y8"

def verify():
    """Connect and verify Python packages."""
    ssh_command = f"ssh -o StrictHostKeyChecking=no -p {PORT} {USER}@{HOST}"
    
    try:
        child = pexpect.spawn(ssh_command, timeout=60, encoding='utf-8')
        child.logfile = sys.stdout
        
        index = child.expect(['password:', 'Password:', pexpect.EOF], timeout=10)
        if index == 0 or index == 1:
            child.sendline(PASSWORD)
            child.expect([r'\$', r'#', r'>'], timeout=30)
        
        print("\n" + "=" * 60)
        print("VERIFICATION REPORT")
        print("=" * 60 + "\n")
        
        # Check Python version
        child.sendline("python3 --version")
        child.expect([r'\$', r'#', r'>'], timeout=10)
        print()
        
        # Check Playwright
        child.sendline("python3 -m playwright --version")
        child.expect([r'\$', r'#', r'>'], timeout=10)
        print()
        
        # List installed packages
        child.sendline("pip3 list | grep -E '(playwright|pandas|reportlab|redis|SpeechRecognition|pydub|ffmpeg)'")
        child.expect([r'\$', r'#', r'>'], timeout=10)
        print()
        
        # Check if Chromium is installed
        child.sendline("ls -la ~/.cache/ms-playwright/ 2>/dev/null | head -5 || echo 'Checking Chromium installation...'")
        child.expect([r'\$', r'#', r'>'], timeout=10)
        print()
        
        # Check system dependencies
        child.sendline("python3 -m playwright install-deps chromium 2>&1 | head -10 || echo 'System deps check'")
        child.expect([r'\$', r'#', r'>'], timeout=15)
        print()
        
        print("\n" + "=" * 60)
        print("Verification complete!")
        print("=" * 60 + "\n")
        
        child.sendline("exit")
        child.expect(pexpect.EOF, timeout=10)
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    verify()

