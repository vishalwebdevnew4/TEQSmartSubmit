# Virtual Display Quick Start

## What is Virtual Display?

Virtual Display allows the browser to render on a **virtual screen** (Xvfb) instead of requiring a physical monitor. This means:
- ✅ Browser can render fully (better for CAPTCHA solving)
- ✅ No visible browser windows (still "headless" from user perspective)  
- ✅ Works on remote servers without displays
- ✅ Better CAPTCHA solving than pure headless mode

## Quick Setup

### 1. Install Xvfb

**With sudo:**
```bash
sudo apt-get update
sudo apt-get install -y xvfb
```

**Without sudo:**
Ask your system administrator or use a container with Xvfb pre-installed.

### 2. Enable in Template

Add to your template JSON:

```json
{
  "use_virtual_display": true,
  "headless": true
}
```

### 3. Test

```bash
cd /var/www/html/TEQSmartSubmit/automation
python3 test_virtual_display.py
```

## How to Use

### From Dashboard

1. Go to Templates
2. Edit your template
3. Add `use_virtual_display: true` to template settings
4. Set `headless: true`
5. Save and run

### From API

Include in your template:
```json
{
  "use_virtual_display": true,
  "headless": true
}
```

### From Environment Variable

```bash
export TEQ_USE_VIRTUAL_DISPLAY=true
```

## How It Works

```
┌─────────────────────────────────────────┐
│  Automation Request                     │
│  (headless: true,                      │
│   use_virtual_display: true)            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Start Xvfb on Display :99              │
│  (Virtual Screen 1920x1080)              │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Set DISPLAY=:99                        │
│  Launch Browser (headless=false)        │
│  Browser renders to virtual display     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Run Automation                         │
│  (CAPTCHA solving works better!)        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Cleanup: Stop Xvfb                     │
└─────────────────────────────────────────┘
```

## Benefits

| Feature | Pure Headless | Virtual Display |
|---------|---------------|-----------------|
| Speed | ⚡ Fastest | ⚡ Fast |
| CAPTCHA Solving | ⚠️ Limited | ✅ Better |
| Resource Usage | 💚 Low | 💛 Medium |
| Visibility | ❌ None | ✅ Can view with VNC |
| Setup | ✅ None | ⚙️ Requires Xvfb |

## Troubleshooting

### "Xvfb not found"
```bash
sudo apt-get install xvfb
```

### "Display :99 already in use"
This is fine - the system will reuse it. To manually stop:
```bash
pkill -f "Xvfb :99"
```

### Still running in headless mode?
1. Check `use_virtual_display: true` is set
2. Check Xvfb is installed: `which Xvfb`
3. Check logs for virtual display messages

## Viewing Virtual Display (Optional)

If you want to see what's happening:

```bash
# Install VNC server
sudo apt-get install x11vnc

# Start VNC on virtual display
export DISPLAY=:99
x11vnc -display :99 -nopw -listen localhost

# Connect with VNC client
vncviewer localhost:5900
```

## Performance

- **Memory**: ~50-100MB for Xvfb
- **CPU**: Negligible
- **Startup**: ~0.5-1 second

## When to Use

✅ **Use Virtual Display when:**
- CAPTCHA solving is failing in pure headless mode
- You need better browser rendering
- Running on remote server without display

❌ **Use Pure Headless when:**
- CAPTCHA solving works fine
- Maximum speed is priority
- Minimal resource usage needed

## More Information

See `VIRTUAL_DISPLAY_SETUP.md` for detailed documentation.

