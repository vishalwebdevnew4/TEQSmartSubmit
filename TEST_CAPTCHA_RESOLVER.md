# Testing CAPTCHA Resolver

This guide will help you test and verify that the CAPTCHA resolver is working correctly.

## Quick Start

### Step 1: Check Dependencies

```bash
python3 check_captcha_dependencies.py
```

This will check if all required dependencies are installed.

### Step 2: Install Missing Dependencies (if needed)

```bash
# Install Python packages
pip install SpeechRecognition pydub playwright

# Install playwright browsers
playwright install chromium

# Install system dependencies (for audio processing)
# Ubuntu/Debian:
sudo apt-get install ffmpeg

# macOS:
brew install ffmpeg
```

### Step 3: Run the Test

```bash
python3 test_captcha_resolver.py
```

Choose option 1 for a full automation test, or option 2 for direct solver testing.

## Test Options

### Option 1: Full Automation Test (Recommended)

This test runs a complete automation workflow:
- Navigates to the test URL
- Fills in the form fields
- Automatically solves reCAPTCHA using the local solver
- Submits the form
- Verifies success

**What to expect:**
- The browser runs in headless mode (background)
- If CAPTCHA appears, it will be solved automatically
- Audio challenges will be solved using speech recognition
- The test should complete successfully

**To see the browser:**
Edit `test_captcha_resolver.py` and set `"headless": False` in the template.

### Option 2: Direct Solver Test

This test directly tests the CAPTCHA solver:
- Opens a visible browser window
- Navigates to the test page
- Uses the LocalCaptchaSolver to solve reCAPTCHA
- Verifies the token was extracted

**What to expect:**
- A browser window will open
- You'll see the CAPTCHA being solved automatically
- The test will verify the token was extracted successfully

## Troubleshooting

### "Module not found" errors

```bash
# Make sure you're in the project root directory
cd /var/www/html/TEQSmartSubmit

# Install missing packages
pip install -r automation/requirements_captcha.txt
```

### "playwright not found"

```bash
pip install playwright
playwright install chromium
```

### "ffmpeg not found"

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**CentOS/RHEL:**
```bash
sudo yum install ffmpeg
```

### "Speech recognition failed"

- Check your internet connection (uses Google's free API)
- The audio file might not have downloaded correctly
- Try running with `headless: False` to see what's happening

### CAPTCHA solving takes too long

- Audio challenges can take 30-60 seconds
- Image challenges may not be fully supported yet
- Check the logs for detailed progress

### Test fails with "CAPTCHA not solved"

1. Verify the CAPTCHA solver is enabled in the template:
   ```json
   {
     "use_local_captcha_solver": true
   }
   ```

2. Check that the test URL still has a working CAPTCHA

3. Try running with `headless: False` to see what's happening

4. Check the console output for error messages

## Expected Output

### Successful Test

```
🧪 TESTING CAPTCHA RESOLVER
======================================================================

📋 Test Configuration:
   URL: https://interiordesign.xcelanceweb.com/
   Solver: Local CAPTCHA Solver (fully automated)
   Mode: Headless (can be set to False for visual debugging)

🚀 Starting automation test...
   - Local CAPTCHA solver is ENABLED
   - The solver will automatically handle reCAPTCHA
   - Audio challenges will be solved using speech recognition

... automation runs ...

======================================================================
📊 TEST RESULTS
======================================================================

Status: success
Message: Automation completed successfully...

======================================================================

✅ TEST PASSED: CAPTCHA resolver worked successfully!
```

### Failed Test

If the test fails, check:
1. The error message in the output
2. Dependencies are installed correctly
3. The test URL is accessible
4. Network connectivity for speech recognition API

## Advanced Testing

### Test with Different CAPTCHA Types

Edit the test script to test different URLs with different CAPTCHA types:
- reCAPTCHA v2 (checkbox)
- reCAPTCHA v2 (audio challenge)
- hCaptcha (if implemented)

### Test with API-based Solvers

You can also test with paid API services:
1. Get an API key from 2captcha, AntiCaptcha, etc.
2. Set environment variable: `export CAPTCHA_2CAPTCHA_API_KEY=your_key`
3. Edit template to use: `"captcha_service": "2captcha"`

### Debug Mode

Run with headless=False to see the browser:
```python
template = {
    "headless": False,  # See the browser
    ...
}
```

## Integration Testing

To test the CAPTCHA resolver in the full application:

1. Start the Next.js server:
   ```bash
   npm run dev
   ```

2. Use the dashboard to submit a form with CAPTCHA

3. The CAPTCHA resolver will automatically be used if enabled in the template

## Success Criteria

✅ Test passes if:
- Automation completes without errors
- CAPTCHA is solved automatically (checkbox or audio)
- Form submission succeeds
- Success indicators are detected

❌ Test fails if:
- CAPTCHA cannot be solved
- Dependencies are missing
- Network errors occur
- Form submission fails

## Next Steps

After successful testing:
1. The CAPTCHA resolver is ready for production use
2. You can integrate it into your automation templates
3. Monitor success rates and adjust timeouts as needed

---

**Status**: ✅ Ready for testing!

