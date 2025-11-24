# Google reCAPTCHA Audio Challenge Manual Automation

This script provides **manual automation** for Google reCAPTCHA with automatic audio challenge solving.

## Features

- ✅ **Non-headless mode** (visible browser for inspection)
- ✅ **Automatic audio challenge solving**
- ✅ **CAPTCHA verification**
- ✅ **Comprehensive logging and screenshots**

## Requirements

### Python Dependencies
```bash
pip install SpeechRecognition pydub
```

### System Dependencies
```bash
# Linux
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

## Usage

### Basic Usage
```bash
python3 test_recaptcha_audio_manual.py
```

This will test the default URL: `https://interiordesign.xcelanceweb.com/contact`

### Custom URL
```bash
python3 test_recaptcha_audio_manual.py "https://your-website.com/contact"
```

## How It Works

1. **Navigation**: Opens the URL in a visible browser window
2. **Detection**: Automatically detects Google reCAPTCHA on the page
3. **Checkbox Click**: Clicks the reCAPTCHA checkbox
4. **Audio Challenge**: If an audio challenge appears:
   - Switches to audio mode
   - Downloads the audio file
   - Uses speech recognition to solve it
   - Submits the answer
5. **Verification**: Verifies the CAPTCHA token is present and valid
6. **Screenshots**: Saves screenshots for inspection

## Output

The script provides:
- Real-time progress updates
- Detailed solving steps
- Token verification results
- Screenshots saved to:
  - `recaptcha_solved.png` (on success)
  - `recaptcha_failed.png` (on failure)
  - `recaptcha_error.png` (on error)

## Example Output

```
================================================================================
🤖 GOOGLE RECAPTCHA AUDIO CHALLENGE SOLVER
================================================================================

📍 URL: https://interiordesign.xcelanceweb.com/contact
🖥️  Headless Mode: False (Visible Browser)
🎧 Audio Challenge: Enabled
✅ Verification: Enabled

⏳ Navigating to page...
✅ Page loaded successfully

🔍 Checking for Google reCAPTCHA...
✅ Google reCAPTCHA detected!

🤖 Initializing reCAPTCHA solver with audio challenge support...

🎯 Starting reCAPTCHA solving process...
   Steps:
   1. Click reCAPTCHA checkbox
   2. Detect audio challenge (if presented)
   3. Download and solve audio challenge
   4. Submit answer and verify

--------------------------------------------------------------------------------
📊 SOLVING RESULTS
--------------------------------------------------------------------------------
✅ SUCCESS! reCAPTCHA solved!
   Token: 03AGdBq25...
   Token Length: 2000+ characters
   Solver Used: LocalCaptchaSolver

🔍 Verifying token in page...
   ✅ Token found in page!
   ✅ reCAPTCHA checkbox is checked

📸 Success screenshot saved: recaptcha_solved.png

================================================================================
✅ VERIFICATION COMPLETE - CAPTCHA IS SOLVED!
================================================================================
```

## Troubleshooting

### Audio Recognition Fails
- Ensure `SpeechRecognition` and `pydub` are installed
- Check that `ffmpeg` is installed and in PATH
- Try running with verbose logging

### reCAPTCHA Not Detected
- Wait for dynamic content to load
- Check if reCAPTCHA loads via JavaScript
- Verify the page actually has reCAPTCHA

### Token Not Found
- The token may be in an iframe (this is normal)
- Check the browser console for errors
- Verify the form submission works

## Notes

- The browser stays open for 60 seconds after success for manual inspection
- All screenshots are saved in the script directory
- The script handles multiple retry attempts automatically
- Audio challenges are solved using local speech recognition (no external services)

## Integration

This script can be integrated into your automation workflow:

```python
from test_recaptcha_audio_manual import solve_recaptcha_with_audio

# In your automation code
success = await solve_recaptcha_with_audio(url, headless=False)
if success:
    # Continue with form submission
    pass
```

