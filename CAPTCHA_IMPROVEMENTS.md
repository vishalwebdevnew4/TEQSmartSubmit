# CAPTCHA Solver Improvements

## Overview
The CAPTCHA solver now uses a **hybrid approach** that tries multiple methods to solve CAPTCHAs reliably.

## How It Works

### 1. Hybrid Mode (Default)
- **Step 1**: Try local solver first (free, fully automated)
- **Step 2**: If local solver fails, automatically fallback to external service (2captcha, AntiCaptcha, etc.)
- **Step 3**: If all automated methods fail, wait for manual solving (in non-headless mode)

### 2. Configuration Options

#### In Template JSON:
```json
{
  "use_local_captcha_solver": true,    // Try local solver first
  "use_hybrid_captcha_solver": true,  // Enable hybrid mode (fallback to external)
  "captcha_service": "auto"           // Auto-select best available service
}
```

#### Environment Variables:
- `TEQ_USE_LOCAL_CAPTCHA_SOLVER=true` - Enable local solver
- `TEQ_USE_HYBRID_CAPTCHA_SOLVER=true` - Enable hybrid mode (default: true)
- `CAPTCHA_2CAPTCHA_API_KEY=...` - 2captcha API key
- `CAPTCHA_ANTICAPTCHA_API_KEY=...` - AntiCaptcha API key
- `CAPTCHA_CAPSOLVER_API_KEY=...` - CapSolver API key

### 3. Solver Priority (when `captcha_service: "auto"`)

1. **Local Solver** (if enabled)
   - Free, no API key needed
   - Solves audio challenges using speech recognition
   - Timeout: 60 seconds

2. **External Services** (if local fails or disabled)
   - 2captcha (if API key configured)
   - AntiCaptcha (if API key configured)
   - CapSolver (if API key configured)
   - AI4CAP (if API key configured)

3. **Manual Solving** (if all automated methods fail)
   - Only in non-headless mode
   - Waits up to 5 minutes for user to solve manually

## Benefits

✅ **Reliability**: Multiple fallback options ensure CAPTCHA gets solved
✅ **Cost-effective**: Tries free local solver first
✅ **Flexibility**: Can use only local, only external, or hybrid mode
✅ **No API key required**: Works with just local solver (though less reliable)

## Usage Examples

### Example 1: Local Solver Only
```json
{
  "use_local_captcha_solver": true,
  "use_hybrid_captcha_solver": false,
  "captcha_service": "local"
}
```

### Example 2: Hybrid Mode (Recommended)
```json
{
  "use_local_captcha_solver": true,
  "use_hybrid_captcha_solver": true,
  "captcha_service": "auto"
}
```

### Example 3: External Service Only
```json
{
  "use_local_captcha_solver": false,
  "captcha_service": "2captcha"
}
```

## Troubleshooting

### Local Solver Fails
- Check if `speech_recognition` and `pydub` are installed: `pip install SpeechRecognition pydub`
- Audio challenge might not be loading - check browser console
- Try enabling hybrid mode to fallback to external service

### External Service Fails
- Verify API key is correct
- Check account balance (for paid services)
- Ensure network connectivity

### All Methods Fail
- Check if CAPTCHA type is supported (currently: reCAPTCHA v2, hCaptcha)
- Try manual solving in non-headless mode
- Check browser console for errors

## Future Improvements

- [ ] Better audio challenge detection
- [ ] Support for reCAPTCHA v3
- [ ] Image challenge solving (currently only audio)
- [ ] Caching solved tokens for same site
- [ ] Better error messages and diagnostics

