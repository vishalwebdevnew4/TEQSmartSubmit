# Single Tab Mode - Browser Reuse

## Overview

Single Tab Mode allows you to reuse the same browser tab across multiple URLs. Instead of opening and closing tabs for each URL, the browser stays open and just navigates to new URLs in the same tab.

**Benefits:**
- ✅ Much faster (no browser startup/teardown overhead)
- ✅ Browser runs in background (headless=False with virtual display)
- ✅ Less resource usage
- ✅ Better for processing multiple URLs

## How It Works

1. **Browser starts once** - Creates a single browser instance with one tab
2. **For each URL:**
   - Navigate to URL in existing tab (`page.goto()`)
   - Fill form and submit
   - Navigate to next URL (same tab)
3. **Browser closes** - Only after all URLs are processed

## Usage

### Option 1: Enable in Template

Add to your template JSON:

```json
{
  "reuse_browser": true,
  "headless": false,
  "use_virtual_display": true
}
```

### Option 2: From Command Line

Use the `run_multiple_urls.py` script:

```bash
cd /var/www/html/TEQSmartSubmit/automation

# Process multiple URLs from command line
python3 run_multiple_urls.py \
  --urls "https://example.com/form1,https://example.com/form2,https://example.com/form3" \
  --template template.json

# Or from a file (one URL per line)
python3 run_multiple_urls.py \
  --urls urls.txt \
  --template template.json
```

### Option 3: From Dashboard

1. Edit your template
2. Add `reuse_browser: true`
3. Set `headless: false`
4. Set `use_virtual_display: true`
5. Save and run

## Configuration

### Template Settings

```json
{
  "reuse_browser": true,        // Enable single tab mode
  "headless": false,            // Browser visible but in background
  "use_virtual_display": true,  // Use virtual display for background operation
  "fields": [...],              // Your form fields
  "submit_selector": "..."      // Submit button selector
}
```

### Environment Variables

```bash
export TEQ_REUSE_BROWSER=true
export TEQ_USE_VIRTUAL_DISPLAY=true
```

## How It Runs

```
┌─────────────────────────────────────────┐
│  Start Browser (once)                    │
│  - headless=False (visible)              │
│  - Virtual display (background)          │
│  - Single tab created                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  For Each URL:                          │
│  1. Navigate: page.goto(url)            │
│  2. Fill form                           │
│  3. Submit                              │
│  4. Wait for response                   │
│  5. Navigate to next URL (same tab)     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Close Browser (after all URLs)          │
└─────────────────────────────────────────┘
```

## Performance

**Without Single Tab Mode:**
- Browser startup: ~2-3 seconds per URL
- Browser teardown: ~1 second per URL
- **Total overhead: ~3-4 seconds per URL**

**With Single Tab Mode:**
- Browser startup: ~2-3 seconds (once)
- Navigation: ~0.1 seconds per URL
- Browser teardown: ~1 second (once)
- **Total overhead: ~3-4 seconds total**

**Example: 100 URLs**
- Without: ~400 seconds overhead
- With: ~4 seconds overhead
- **Savings: ~396 seconds (6.6 minutes)**

## Requirements

- Xvfb installed (for virtual display)
- Python 3.8+
- Playwright installed

## Troubleshooting

### Issue: Browser not reusing

**Check:**
1. `reuse_browser: true` is set in template
2. Browser manager is being used
3. Check logs for "Reusing existing browser tab"

### Issue: Browser visible on screen

**Solution:**
- Ensure `use_virtual_display: true` is set
- Browser will render on virtual display (not visible)

### Issue: URLs not processing

**Check:**
1. Browser is staying open (check logs)
2. Navigation is working (check "Navigating to: ..." messages)
3. No errors in logs

## Example

```python
from browser_manager import BrowserManager
from run_submission import run_submission

# Create browser manager
browser_manager = BrowserManager(
    headless=False,           # Visible browser
    use_virtual_display=True  # But in background
)

# Start browser once
await browser_manager.start()

# Process multiple URLs
urls = [
    "https://example.com/form1",
    "https://example.com/form2",
    "https://example.com/form3"
]

for url in urls:
    result = await run_submission(
        url=url,
        template_path=template_path,
        browser_manager=browser_manager  # Reuse browser
    )
    print(f"Result: {result}")

# Close browser once
await browser_manager.stop()
```

## Notes

- Browser stays open between URLs
- Same tab is reused (just URL changes)
- Virtual display keeps browser in background
- Much faster than opening/closing tabs
- Better for batch processing

