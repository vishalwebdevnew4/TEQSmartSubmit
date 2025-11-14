#!/usr/bin/env python3
"""
Complete the Python setup on remote server - finish remaining packages.
"""

import pexpect
import sys
import os

# Server details
HOST = "teqsmartsubmit.xcelanceweb.com"
PORT = "3129"
USER = "teqsmartsftpuser"
PASSWORD = "XFho65rfr@uj()7y8"

# Remaining commands to complete
COMMANDS = [
    "pip3 install --user SpeechRecognition pydub ffmpeg-python",
    "python3 -m playwright --version",
]

SUDO_COMMANDS = [
    "sudo python3 -m playwright install-deps chromium",
]

def run_commands():
    """Connect and complete remaining installations."""
    print("=" * 50)
    print("Completing Python setup on remote server...")
    print("=" * 50)
    
    ssh_command = f"ssh -o StrictHostKeyChecking=no -p {PORT} {USER}@{HOST}"
    
    try:
        child = pexpect.spawn(ssh_command, timeout=600, encoding='utf-8')
        child.logfile = sys.stdout
        
        # Handle password prompt
        index = child.expect(['password:', 'Password:', pexpect.EOF, pexpect.TIMEOUT], timeout=10)
        if index == 0 or index == 1:
            child.sendline(PASSWORD)
            child.expect([r'\$', r'#', r'>'], timeout=30)
        else:
            print("Connection failed")
            return False
        
        print("\nConnected! Running remaining commands...\n")
        
        # Run regular commands
        for cmd in COMMANDS:
            print(f"Running: {cmd}")
            child.sendline(cmd)
            child.expect([r'\$', r'#', r'>'], timeout=600)
            print()
        
        # Run sudo commands
        print("\nInstalling system dependencies (sudo required)...\n")
        for cmd in SUDO_COMMANDS:
            print(f"Running: {cmd}")
            child.sendline(cmd)
            
            while True:
                index = child.expect([
                    'password:',
                    'Password:',
                    r'\[sudo\] password',
                    r'\$',
                    r'#',
                    r'>',
                    pexpect.TIMEOUT
                ], timeout=180)
                
                if index in [0, 1, 2]:
                    child.sendline(PASSWORD)
                elif index in [3, 4, 5]:
                    break
                elif index == 6:
                    print("Timeout, but continuing...")
                    break
            print()
        
        # Final verification
        print("\n" + "=" * 50)
        print("Verification:")
        print("=" * 50)
        
        child.sendline("pip3 list | grep -E '(playwright|pandas|reportlab|redis|SpeechRecognition|pydub)'")
        child.expect([r'\$', r'#', r'>'], timeout=10)
        
        child.sendline("python3 -m playwright --version")
        child.expect([r'\$', r'#', r'>'], timeout=10)
        
        print("\n" + "=" * 50)
        print("Python setup complete!")
        print("=" * 50 + "\n")
        
        child.sendline("exit")
        child.expect(pexpect.EOF, timeout=10)
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = run_commands()
    sys.exit(0 if success else 1)

