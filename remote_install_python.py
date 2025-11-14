#!/usr/bin/env python3
"""
SSH connection script to install Python dependencies on remote server.
This uses pexpect to handle SSH password authentication.
"""

import pexpect
import sys
import os

# Server details
HOST = "teqsmartsubmit.xcelanceweb.com"
PORT = "3129"
USER = "teqsmartsftpuser"
PASSWORD = "XFho65rfr@uj()7y8"

# Python setup commands (without sudo - user install only)
COMMANDS = [
    "pip3 install --user playwright",
    "python3 -m playwright install chromium",
    "pip3 install --user pandas reportlab redis",
    "pip3 install --user SpeechRecognition pydub ffmpeg-python",
    "python3 -m playwright --version",
    "pip3 list | grep -i playwright",
]

# Sudo commands (require password)
SUDO_COMMANDS = [
    "sudo python3 -m playwright install-deps chromium",
]

def run_remote_commands():
    """Connect via SSH and run Python setup commands."""
    print("=" * 50)
    print("Connecting to remote server...")
    print("=" * 50)
    
    # Connect via SSH
    ssh_command = f"ssh -o StrictHostKeyChecking=no -p {PORT} {USER}@{HOST}"
    
    try:
        child = pexpect.spawn(ssh_command, timeout=300, encoding='utf-8')
        child.logfile = sys.stdout
        
        # Handle password prompt
        index = child.expect(['password:', 'Password:', pexpect.EOF, pexpect.TIMEOUT], timeout=10)
        
        if index == 0 or index == 1:
            child.sendline(PASSWORD)
            child.expect([r'\$', r'#', r'>'], timeout=30)
        elif index == 2:
            print("Connection failed: EOF")
            return False
        elif index == 3:
            print("Connection timeout")
            return False
        
        print("\n" + "=" * 50)
        print("Connected! Starting Python setup...")
        print("=" * 50 + "\n")
        
        # Navigate to project directory (try common paths)
        child.sendline("cd /var/www/html/TEQSmartSubmit 2>/dev/null || cd ~/TEQSmartSubmit 2>/dev/null || pwd")
        child.expect([r'\$', r'#', r'>'], timeout=10)
        
        # Run each command
        for i, cmd in enumerate(COMMANDS, 1):
            print(f"\n[{i}/{len(COMMANDS)}] Running: {cmd}")
            print("-" * 50)
            
            child.sendline(cmd)
            
            # Wait for command to complete or password prompt for sudo
            while True:
                try:
                    index = child.expect([
                        'password:',
                        'Password:',
                        r'\$',
                        r'#',
                        r'>',
                        pexpect.TIMEOUT,
                        pexpect.EOF
                    ], timeout=300)
                    
                    if index == 0 or index == 1:
                        # Sudo password prompt
                        child.sendline(PASSWORD)
                    elif index in [2, 3, 4]:
                        # Command completed (prompt received)
                        break
                    elif index == 5:
                        print("Command timeout, continuing...")
                        break
                    elif index == 6:
                        print("Connection closed")
                        return False
                except pexpect.TIMEOUT:
                    print("Timeout waiting for command, continuing...")
                    break
                except pexpect.EOF:
                    print("Connection closed unexpectedly")
                    return False
        
        # Run sudo commands
        print("\n" + "=" * 50)
        print("Installing system dependencies (requires sudo)...")
        print("=" * 50 + "\n")
        
        for i, cmd in enumerate(SUDO_COMMANDS, 1):
            print(f"\n[Sudo {i}/{len(SUDO_COMMANDS)}] Running: {cmd}")
            print("-" * 50)
            
            child.sendline(cmd)
            
            # Wait for sudo password prompt
            while True:
                try:
                    index = child.expect([
                        'password:',
                        'Password:',
                        r'\[sudo\] password',
                        r'\$',
                        r'#',
                        r'>',
                        pexpect.TIMEOUT,
                        pexpect.EOF
                    ], timeout=120)
                    
                    if index in [0, 1, 2]:
                        # Sudo password prompt
                        print("Providing sudo password...")
                        child.sendline(PASSWORD)
                    elif index in [3, 4, 5]:
                        # Command completed
                        break
                    elif index == 6:
                        print("Command timeout, continuing...")
                        break
                    elif index == 7:
                        print("Connection closed")
                        return False
                except pexpect.TIMEOUT:
                    print("Timeout, continuing...")
                    break
                except pexpect.EOF:
                    print("Connection closed")
                    return False
        
        print("\n" + "=" * 50)
        print("Python setup complete!")
        print("=" * 50 + "\n")
        
        # Final verification
        child.sendline("python3 -m playwright --version")
        child.expect([r'\$', r'#', r'>'], timeout=10)
        
        child.sendline("pip3 list | grep -E '(playwright|pandas|reportlab|redis|SpeechRecognition|pydub)'")
        child.expect([r'\$', r'#', r'>'], timeout=10)
        
        # Exit SSH
        child.sendline("exit")
        child.expect(pexpect.EOF, timeout=10)
        
        return True
        
    except pexpect.ExceptionPexpect as e:
        print(f"Error: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\nInstallation interrupted by user")
        return False

if __name__ == "__main__":
    # Check if pexpect is installed
    try:
        import pexpect
    except ImportError:
        print("Error: pexpect is required. Install it with: pip3 install pexpect")
        sys.exit(1)
    
    success = run_remote_commands()
    sys.exit(0 if success else 1)

