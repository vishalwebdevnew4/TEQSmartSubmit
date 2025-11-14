# Buster Extension Integration Guide

Based on the article: https://medium.com/analytics-vidhya/how-to-easily-bypass-recaptchav2-with-selenium-7f7a9a44fa9e

## Overview

Buster is a browser extension that automatically solves reCAPTCHA v2 audio challenges. It can be integrated with Playwright to provide an alternative to our custom audio recognition solution.

## How Buster Works

1. **Extension Installation**: Buster is a Chrome/Firefox extension that uses audio recognition
2. **Automatic Solving**: When an audio challenge appears, Buster automatically solves it
3. **Solver Button**: Buster adds a `#solver-button` that can be clicked programmatically

⚠️ **Important Note**: As of 2021, Buster's `solver-button` is now contained in a **closed shadow DOM** (see [issue #273](https://github.com/dessant/buster/issues/273)). This makes it harder to access programmatically. The code attempts to access it through shadow DOM, but it may not always work.

## Integration Options

### Option 1: Use Buster Extension (Recommended for easier setup)

**Pros:**
- No need for Python speech recognition libraries
- Handles audio recognition automatically
- Well-tested and maintained

**Cons:**
- Requires browser extension installation
- Less control over the solving process

**Setup:**
1. Download Buster extension from: https://github.com/dessant/buster
2. Load it into Playwright browser context
3. The code will automatically detect and use it

### Option 2: Current Implementation (Self-made solver)

**Pros:**
- Full control over the solving process
- No external dependencies (except speech_recognition)
- Works without browser extensions

**Cons:**
- Requires `SpeechRecognition` and `pydub` libraries
- May need fine-tuning for different audio qualities

## Current Implementation

Our code now supports both approaches:

1. **Buster Detection**: Automatically detects if Buster extension is loaded
2. **Fallback**: If Buster is not available, uses our custom audio recognition
3. **Best of Both**: Tries Buster first, then falls back to manual solving

## Loading Buster Extension in Playwright

To use Buster with Playwright, you would need to:

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    # For Chromium
    context = await p.chromium.launch_persistent_context(
        user_data_dir="/path/to/user/data",
        headless=False,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--load-extension=/path/to/buster-extension'
        ]
    )
    
    # Or for Firefox
    context = await p.firefox.launch_persistent_context(
        user_data_dir="/path/to/user/data",
        headless=False,
        firefox_user_prefs={
            'xpinstall.signatures.required': False
        }
    )
```

## Recommendation

For now, our current implementation (self-made solver) is working and doesn't require browser extensions. However, if you want to use Buster:

1. Install Buster extension in a browser profile
2. Use persistent context in Playwright
3. The code will automatically detect and use Buster when available

The current code already has Buster detection built in - it will try to use Buster if available, otherwise falls back to our custom solver.

