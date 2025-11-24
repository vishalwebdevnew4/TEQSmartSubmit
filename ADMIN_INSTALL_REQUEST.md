# Server Admin Installation Request

## Required Package Installation

The automation system requires **Xvfb** (X Virtual Framebuffer) to run browsers in visible mode for CAPTCHA verification.

## Installation Command

Please run this command on the server:

```bash
sudo apt-get update
sudo apt-get install -y xvfb
```

## What This Installs

- **Xvfb**: Virtual display server that allows GUI applications to run on headless servers
- **xvfb-run**: Wrapper script that automatically manages Xvfb (this is what we'll use)

## Why It's Needed

The automation needs to:
1. Launch browsers in visible mode (not headless)
2. Allow manual CAPTCHA verification
3. Work on servers without physical displays

Xvfb creates a virtual display that makes the browser think it has a screen, even on headless servers.

## Verification

After installation, verify with:
```bash
which xvfb-run
# Should show: /usr/bin/xvfb-run
```

## Impact

- **One-time installation** - no recurring maintenance
- **Small package** - minimal disk space (~5MB)
- **No security concerns** - standard system package
- **No configuration needed** - works automatically after installation

## Alternative (if apt-get not available)

For CentOS/RHEL:
```bash
sudo yum install -y xorg-x11-server-Xvfb
```

Thank you!

