# Installing Playwright Browsers on Remote Server

If you see errors like "Failed to launch chromium" or "Executable doesn't exist", you need to install Playwright browser binaries on your remote server.

## Quick Installation

### Step 1: Install Playwright Python Package
```bash
pip install playwright
# OR if using system Python:
pip3 install playwright
```

### Step 2: Install Browser Binaries (REQUIRED)
```bash
# Install Chromium (recommended)
playwright install chromium

# OR install all browsers
playwright install

# OR if using system Python:
python3 -m playwright install chromium
```

### Step 3: Install System Dependencies (for headless mode on Linux)

#### Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y \
  libnss3 \
  libatk1.0-0 \
  libatk-bridge2.0-0 \
  libcups2 \
  libdrm2 \
  libxkbcommon0 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxrandr2 \
  libgbm1 \
  libasound2
```

#### CentOS/RHEL:
```bash
sudo yum install -y \
  nss \
  atk \
  at-spi2-atk \
  cups-libs \
  libdrm \
  libxkbcommon \
  libXcomposite \
  libXdamage \
  libXfixes \
  libXrandr \
  mesa-libgbm \
  alsa-lib
```

## Verify Installation

After installation, verify that browsers are available:

```bash
python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print('✅ Playwright browsers installed successfully'); p.stop()"
```

## Troubleshooting

### If you get permission errors:
- Make sure you have write permissions to the Playwright cache directory (usually `~/.cache/ms-playwright`)
- Try running with `sudo` if needed (though not recommended for production)

### If browsers still don't work:
- Check that the Playwright installation path is correct
- Verify Python environment matches the one used by your application
- Check system logs for additional error messages

### For Docker/Container environments:
- Install browsers during image build
- Ensure all system dependencies are included in your Dockerfile

## Notes

- Browser binaries are large (~300MB for Chromium)
- Installation may take a few minutes depending on your connection
- Browsers are installed in `~/.cache/ms-playwright/` by default

