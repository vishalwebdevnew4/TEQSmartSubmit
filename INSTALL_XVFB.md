# Installing Xvfb for Visible Browser Mode

Since you need to verify CAPTCHAs manually, the browser must run in visible mode. On headless servers (without a display), we use **Xvfb** (X Virtual Framebuffer) to create a virtual display.

## Quick Installation

### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y xvfb
```

### CentOS/RHEL:
```bash
sudo yum install -y xorg-x11-server-Xvfb
```

## Verify Installation

After installation, verify Xvfb is available:
```bash
which Xvfb
# Should show: /usr/bin/Xvfb
```

## How It Works

1. **Automatically detects** if no DISPLAY is available
2. **Starts Xvfb** virtual display (e.g., `:99`)
3. **Sets DISPLAY environment variable** to the virtual display
4. **Launches browser** in visible mode (headless=False)
5. **Cleans up** Xvfb when done

## Manual Testing

You can test Xvfb manually:
```bash
# Start Xvfb on display :99
Xvfb :99 -screen 0 1280x720x24 &

# Set DISPLAY
export DISPLAY=:99

# Test with a simple command
xclock &  # If xclock is installed

# Stop Xvfb
killall Xvfb
```

## Troubleshooting

### "Xvfb not found"
- Install Xvfb using the commands above
- Make sure you have sudo/root access

### "Permission denied"
- Xvfb needs to be able to create display sockets
- Usually works fine with default permissions

### "Display already in use"
- The automation automatically finds an available display number (99-199)
- If you see this, try a different display number manually

## Notes

- Xvfb creates a virtual display that you can't see, but the browser thinks it's visible
- This allows the browser to run in "visible" mode even on headless servers
- Perfect for CAPTCHA verification where you need the browser to think it's visible
- The automation handles all of this automatically - you just need Xvfb installed

