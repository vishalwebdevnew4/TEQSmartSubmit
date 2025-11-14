#!/usr/bin/env python3
"""
Check Python installation on remote server.
"""

import pexpect
import sys

HOST = "teqsmartsubmit.xcelanceweb.com"
PORT = "3129"
USER = "teqsmartsftpuser"
PASSWORD = "XFho65rfr@uj()7y8"

def check_python():
    """Check Python installation status."""
    ssh_command = f"ssh -o StrictHostKeyChecking=no -p {PORT} {USER}@{HOST}"
    
    try:
        child = pexpect.spawn(ssh_command, timeout=60, encoding='utf-8')
        child.logfile = sys.stdout
        
        index = child.expect(['password:', 'Password:', pexpect.EOF], timeout=10)
        if index == 0 or index == 1:
            child.sendline(PASSWORD)
            child.expect([r'\$', r'#', r'>'], timeout=30)
        
        print("\n" + "=" * 70)
        print("PYTHON INSTALLATION CHECK ON REMOTE SERVER")
        print("=" * 70 + "\n")
        
        # Check multiple Python paths
        checks = [
            ("python3", "python3 --version"),
            ("python3.10", "python3.10 --version 2>&1 || echo 'Not found'"),
            ("python3.9", "python3.9 --version 2>&1 || echo 'Not found'"),
            ("python3.8", "python3.8 --version 2>&1 || echo 'Not found'"),
            ("python", "python --version 2>&1 || echo 'Not found'"),
            ("which python3", "which python3"),
            ("pip3", "pip3 --version 2>&1 || echo 'pip3 not found'"),
            ("pip", "pip --version 2>&1 || echo 'pip not found'"),
        ]
        
        results = {}
        for name, cmd in checks:
            print(f"Checking {name}...")
            child.sendline(cmd)
            child.expect([r'\$', r'#', r'>'], timeout=10)
            print()
        
        # Check Python path
        child.sendline("echo $PATH")
        child.expect([r'\$', r'#', r'>'], timeout=5)
        print()
        
        # Check if packages are accessible
        child.sendline("python3 -c 'import sys; print(f\"Python Path: {sys.executable}\")' 2>&1")
        child.expect([r'\$', r'#', r'>'], timeout=10)
        print()
        
        print("=" * 70)
        print("Check complete!")
        print("=" * 70 + "\n")
        
        child.sendline("exit")
        child.expect(pexpect.EOF, timeout=10)
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_python()

