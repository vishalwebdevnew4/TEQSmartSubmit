# How to Check Playwright Installation

## Quick Check

Run the diagnostic script to see what's installed and what's missing:

```bash
cd /var/www/html/TEQSmartSubmit
python3 check_playwright_installation.py
```

## What the Script Checks

1. **Python Environment** - Python version and executable path
2. **System Commands** - Checks for `python3`, `pip`, `pip3`, and `playwright` CLI
3. **Python Packages** - Verifies if `playwright` package is installed
4. **Playwright Browsers** - Checks if browser binaries (chromium, firefox, webkit) are installed
5. **System Dependencies** - Checks Linux system libraries required for headless browsers

## Understanding the Output

### ✅ Green checkmarks = Installed
- Everything with a ✅ is already installed and ready to use

### ❌ Red X = Missing
- Items marked with ❌ need to be installed
- The script will show you the exact commands to run

### ⚠️ Yellow warnings = Issues
- These indicate potential problems that might need attention

## Example Output

```
✅ Playwright Python package: INSTALLED
❌ Playwright browsers: MISSING (chromium)
✅ System dependencies: INSTALLED
```

This means:
- Playwright Python package is installed ✅
- Browser binaries are missing ❌ (need to install)
- System dependencies are fine ✅

## After Running the Script

The script will automatically show you the installation commands you need to run. Just copy and paste them!

## Manual Checks (Alternative)

If you prefer to check manually:

### Check if Playwright is installed:
```bash
python3 -c "import playwright; print('✅ Playwright installed')"
```

### Check if browsers are installed:
```bash
python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print('✅ Browsers installed'); p.stop()"
```

### Check browser location:
```bash
python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print(p.chromium.executable_path); p.stop()"
```

## Troubleshooting

### Script doesn't run:
- Make sure you have Python 3 installed: `python3 --version`
- Make sure the script is executable: `chmod +x check_playwright_installation.py`

### Script shows errors:
- Check Python permissions
- Verify you're using the correct Python environment
- Make sure you have internet connection (for checking packages)

## Next Steps

After running the diagnostic:
1. Review the summary section
2. Copy the installation commands shown
3. Run them on your server
4. Run the diagnostic again to verify installation

