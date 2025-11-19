# Deployment Guide

## Running on Remote Server (No Display)

When deploying to a remote server without a graphical display, the automation will automatically detect this and run in headless mode.

### Automatic Detection

The system automatically detects if a display is available:
- **Local development** (with X11/display): Runs with visible browser (better for CAPTCHA solving)
- **Remote server** (no display): Automatically uses headless mode

### Manual Configuration

If you need to force headless mode, set environment variable:

```bash
export TEQ_FORCE_HEADLESS=true
```

Or in your `.env` file:
```
TEQ_FORCE_HEADLESS=true
```

### Using Virtual Display (Xvfb) - Optional

If you want to run with a visible browser on a remote server (for better CAPTCHA solving), you can set up a virtual display:

#### Install Xvfb:
```bash
sudo apt-get update
sudo apt-get install -y xvfb
```

#### Run with Xvfb:
```bash
# Start Xvfb in background
Xvfb :99 -screen 0 1920x1080x24 &

# Set DISPLAY environment variable
export DISPLAY=:99

# Now run your application
npm run dev
# or
npm start
```

#### Using systemd service (recommended for production):

Create `/etc/systemd/system/xvfb.service`:
```ini
[Unit]
Description=Virtual Frame Buffer X Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable xvfb
sudo systemctl start xvfb
```

Then set DISPLAY in your application environment:
```bash
export DISPLAY=:99
```

### Environment Variables

- `DISPLAY` - X11 display (e.g., `:0` or `:99`)
- `TEQ_FORCE_HEADLESS` - Force headless mode (`true`/`false`)
- `HEADLESS` - Alternative way to force headless mode
- `TEQ_PLAYWRIGHT_HEADLESS` - Playwright-specific headless setting

### Testing

To test if display is available:
```bash
echo $DISPLAY
# Should show something like :0 or :99 if display is available
```

To test headless mode:
```bash
# Force headless
export TEQ_FORCE_HEADLESS=true
# Run your automation
```

### Notes

- **Headless mode**: Works on any server but CAPTCHA solving may be less reliable
- **Non-headless mode**: Requires display (X11) or virtual display (Xvfb), better CAPTCHA solving
- The system automatically chooses the best mode based on environment

