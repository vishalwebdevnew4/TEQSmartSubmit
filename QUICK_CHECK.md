# Quick Server Check

## Run This on Your Server

After SSH'ing into your server, run:

```bash
cd /var/www/html/TEQSmartSubmit
bash check_server_setup.sh
```

Or if the file isn't there yet, run these commands manually:

```bash
# Check DISPLAY
echo "DISPLAY: $DISPLAY"

# Check xvfb-run (best option - no sudo needed if installed)
which xvfb-run

# Check Xvfb
which Xvfb

# Check Python
python3 --version

# Check Playwright
python3 -c "import playwright; print('Playwright installed')"

# Check Playwright browsers
python3 -c "from playwright.sync_api import sync_playwright; p = sync_playwright().start(); print('Chromium:', p.chromium.executable_path); p.stop()"
```

## What to Look For

### ✅ Good Signs:
- `xvfb-run` shows a path → **Will work automatically!**
- `DISPLAY` is set → **Will use existing display**
- `Xvfb` shows a path → **Will work automatically**

### ❌ Issues:
- All show "not found" → **Need to ask admin to install xvfb**

## After Running the Check

1. **If xvfb-run is found**: You're all set! The automation will use it automatically.

2. **If nothing is found**: Ask your server admin to run:
   ```bash
   sudo apt-get install xvfb
   ```

3. **If DISPLAY is set**: The automation will use your existing display session.

## Next Steps

After checking, restart your application:
```bash
pm2 restart all
```

Then test the automation - it should work if xvfb-run is available!

