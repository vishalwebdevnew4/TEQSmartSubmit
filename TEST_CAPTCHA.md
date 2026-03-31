# Testing CAPTCHA Solving - Quick Guide

## ✅ What's Working

The automation script now supports:
- ✅ Automatic CAPTCHA detection
- ✅ Manual CAPTCHA solving (FREE for development)
- ✅ Automatic CAPTCHA solving (with 2captcha API key)

## 🧪 How to Test Manual CAPTCHA Solving

### Method 1: Via API (Recommended)

1. **Set development mode** in your request:
   ```json
   {
     "headless": false,
     "captcha_timeout_ms": 300000,
     ...
   }
   ```

2. **Run automation** from dashboard or API:
   - Browser window will open
   - Form will be filled automatically
   - When CAPTCHA appears, solve it manually
   - Script waits up to 5 minutes
   - After solving, form submits automatically

### Method 2: Direct Python Test

```bash
cd /var/www/html/TEQSmartSubmit
python3 test_captcha.py
```

## 📝 Step-by-Step Test Process

1. **Start the test** - Run automation with `headless: false`
2. **Browser opens** - You'll see a Chrome/Chromium window
3. **Form fills** - Fields are filled automatically
4. **CAPTCHA appears** - You'll see the reCAPTCHA widget
5. **Solve manually** - Click the CAPTCHA checkbox and solve any challenges
6. **Wait for detection** - Script detects when CAPTCHA is solved (checks every few seconds)
7. **Form submits** - After CAPTCHA is solved, form submits automatically
8. **Check result** - Success/error message is returned

## ⚙️ Configuration Options

### Environment Variables (`.env.local`):
```bash
# For visible browser (manual CAPTCHA solving)
HEADLESS=false

# For automatic CAPTCHA solving (requires paid API key)
CAPTCHA_2CAPTCHA_API_KEY=your-api-key-here
```

### Template JSON:
```json
{
  "headless": false,              // Show browser window
  "captcha_timeout_ms": 300000,   // 5 minutes for manual solving
  "captcha_api_key": "...",       // Optional: 2captcha API key
  ...
}
```

## 🔍 Troubleshooting

### CAPTCHA not detected?
- Make sure you're on a page with reCAPTCHA
- Check browser console for errors
- Verify form is fully loaded

### CAPTCHA solved but form still fails?
- Token might not be injected correctly
- Check if form requires additional validation
- Verify CAPTCHA response field is present

### Browser doesn't open?
- Check `HEADLESS=false` is set correctly
- Verify you have display/X11 available (for Linux servers)
- Try running with `DISPLAY=:0` environment variable

## 🎯 Expected Behavior

**With Manual Solving (`headless: false`):**
- Browser window opens ✅
- Form fills automatically ✅
- Script waits for you to solve CAPTCHA ✅
- After solving, form submits ✅

**With Automatic Solving (API key set):**
- Browser runs in background ✅
- CAPTCHA solved automatically via 2captcha ✅
- Form submits without manual intervention ✅

## 💡 Tips

- For development: Use `headless: false` to see what's happening
- For production: Use `headless: true` with API key for automation
- Test timeout: Set `captcha_timeout_ms` to 300000 (5 min) for manual solving
- Production timeout: Set `captcha_timeout_ms` to 60000 (1 min) for automatic solving

