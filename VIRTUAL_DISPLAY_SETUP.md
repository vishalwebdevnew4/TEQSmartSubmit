# Virtual Display Setup Guide

## Overview

Virtual Display allows the browser to render on a virtual screen (Xvfb) instead of requiring a physical monitor. This provides the benefits of:
- ✅ Better CAPTCHA solving (browser can render fully)
- ✅ No visible browser windows (still "headless" from user perspective)
- ✅ Works on remote servers without physical displays
- ✅ Can be viewed remotely if needed (using VNC/X11 forwarding)

## Installation

### With Sudo (Recommended)

```bash
sudo apt-get update
sudo apt-get install -y xvfb x11-utils
```

### Without Sudo

If you don't have sudo access, you can try installing Xvfb from source or use a pre-built binary. However, Xvfb typically requires system-level access. For no-sudo environments, you may need to:

1. Ask your system administrator to install Xvfb
2. Use a containerized environment with Xvfb pre-installed
3. Use a different approach (pure headless mode)

## Usage

### Option 1: Enable in Template

Add to your template JSON:

```json
{
  "use_virtual_display": true,
  "headless": true
}
```

Or using camelCase:

```json
{
  "useVirtualDisplay": true,
  "headless": true
}
```

### Option 2: Enable via Environment Variable

```bash
export TEQ_USE_VIRTUAL_DISPLAY=true
```

### Option 3: Automatic (When Headless + No Display)

The system will automatically attempt to use a virtual display when:
- `headless: true` is set
- `use_virtual_display: true` is set
- No physical display is available

## How It Works

1. When `use_virtual_display: true` is set and headless mode is enabled
2. The system checks if Xvfb is available
3. If available, starts Xvfb on display `:99`
4. Sets `DISPLAY=:99` environment variable
5. Browser runs in non-headless mode but renders to virtual display
6. Virtual display is automatically cleaned up after automation completes

## Testing

### Test Virtual Display

```bash
cd /var/www/html/TEQSmartSubmit/automation
python3 virtual_display.py
```

Expected output:
```
Testing Virtual Display Manager...
✅ Virtual display is running on :99
   DISPLAY=:99
✅ Display is accessible
Test complete.
```

### Test with Automation

```bash
cd /var/www/html/TEQSmartSubmit/automation
python3 run_submission.py \
  --url "https://example.com/form" \
  --template template.json
```

Where `template.json` contains:
```json
{
  "use_virtual_display": true,
  "headless": true,
  "fields": []
}
```

## Viewing Virtual Display (Optional)

If you want to view what's happening on the virtual display:

### Using VNC

1. Install VNC server:
   ```bash
   sudo apt-get install -y tigervnc-standalone-server
   ```

2. Start VNC server on virtual display:
   ```bash
   export DISPLAY=:99
   x11vnc -display :99 -nopw -listen localhost -xkb
   ```

3. Connect with VNC client:
   ```bash
   vncviewer localhost:5900
   ```

### Using X11 Forwarding (SSH)

```bash
ssh -X user@server
export DISPLAY=:99
# Run automation
```

## Troubleshooting

### Issue: "Xvfb not found"

**Solution:**
```bash
sudo apt-get install xvfb
```

### Issue: "Display :99 is already in use"

**Solution:**
The display is already running (possibly from a previous session). This is fine - the system will reuse it.

To manually stop it:
```bash
pkill -f "Xvfb :99"
```

### Issue: "Failed to start Xvfb"

**Possible causes:**
1. Xvfb not installed
2. Display number already in use
3. Insufficient permissions

**Solutions:**
1. Install Xvfb: `sudo apt-get install xvfb`
2. Use a different display number (edit `virtual_display.py`)
3. Check permissions: `ls -la /tmp/.X11-unix/`

### Issue: "Browser still runs in headless mode"

**Check:**
1. Is `use_virtual_display: true` set in template?
2. Is Xvfb installed and accessible?
3. Check logs for virtual display startup messages

### Issue: "CAPTCHA solving still fails"

Virtual display helps but doesn't guarantee CAPTCHA solving. Other factors:
- CAPTCHA complexity
- Network latency
- Browser detection (stealth features help)

## Performance

Virtual display adds minimal overhead:
- Memory: ~50-100MB for Xvfb
- CPU: Negligible (only when rendering)
- Startup time: ~0.5-1 second

## Best Practices

1. **Use virtual display for production** when you need better CAPTCHA solving
2. **Use pure headless** for maximum speed (if CAPTCHA solving works)
3. **Monitor resource usage** - virtual displays use memory
4. **Clean up properly** - the system handles this automatically, but you can manually stop displays if needed

## Configuration

### Change Display Number

Edit `automation/virtual_display.py`:

```python
vdisplay = ensure_virtual_display(display_num=99)  # Change 99 to another number
```

### Change Resolution

Edit `automation/virtual_display.py`:

```python
vdisplay = VirtualDisplay(
    display_num=99,
    width=1920,   # Change width
    height=1080,  # Change height
    depth=24      # Change color depth
)
```

## Integration with Dashboard

To enable virtual display from the dashboard:

1. Edit template in dashboard
2. Add `use_virtual_display: true` to template settings
3. Set `headless: true` (virtual display will be used automatically)
4. Save and run automation

The API route will pass these settings to `run_submission.py`.

## Security Notes

- Virtual displays are isolated and not accessible from outside the server
- Xvfb runs with `-nolisten tcp` for security
- No network ports are opened by default
- If using VNC, ensure proper authentication

## References

- [Xvfb Documentation](https://www.x.org/releases/X11R7.6/doc/man/man1/Xvfb.1.xhtml)
- [Playwright Headless Mode](https://playwright.dev/python/docs/browsers#headed--headless-mode)

