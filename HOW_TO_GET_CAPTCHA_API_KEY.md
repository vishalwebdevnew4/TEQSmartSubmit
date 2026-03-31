# How to Get CAPTCHA API Keys

This guide explains how to get API keys from CAPTCHA solving services. **Note: You don't need these if you're using the free local solver!**

## Quick Answer

**You DON'T need an API key if:**
- ✅ You're using the **local solver** (free, already working)
- ✅ You're testing in development (use `HEADLESS=false` for manual solving)

**You DO need an API key if:**
- ❌ You want to solve **image challenges** automatically
- ❌ You want to use paid services instead of the local solver

---

## Option 1: 2captcha (Most Popular)

### Steps:
1. **Sign up**: Go to [https://2captcha.com](https://2captcha.com)
2. **Create account**: Click "Sign Up" and create an account
3. **Add funds**: Add money to your account (minimum ~$3)
   - Pricing: ~$2.99 per 1000 CAPTCHAs
   - You can start with $5-10 for testing
4. **Get API key**:
   - Go to your account dashboard
   - Find "API Key" section
   - Copy your API key (looks like: `1234567890abcdef1234567890abcdef`)

### Add to `.env.local`:
```bash
CAPTCHA_2CAPTCHA_API_KEY=your-api-key-here
# or
TEQ_CAPTCHA_API_KEY=your-api-key-here
```

---

## Option 2: AntiCaptcha

### Steps:
1. **Sign up**: Go to [https://anti-captcha.com](https://anti-captcha.com)
2. **Create account**: Register for a new account
3. **Add funds**: Deposit money (minimum varies)
   - Pricing: ~$1.00 per 1000 CAPTCHAs (cheaper than 2captcha)
4. **Get API key**:
   - Go to Settings → API
   - Copy your API key

### Add to `.env.local`:
```bash
CAPTCHA_ANTICAPTCHA_API_KEY=your-api-key-here
```

---

## Option 3: CapSolver

### Steps:
1. **Sign up**: Go to [https://capsolver.com](https://capsolver.com)
2. **Create account**: Register for a new account
3. **Add funds**: Deposit money
4. **Get API key**:
   - Go to your dashboard
   - Find API Key section
   - Copy your API key

### Add to `.env.local`:
```bash
CAPTCHA_CAPSOLVER_API_KEY=your-api-key-here
```

---

## Pricing Comparison

| Service | Price per 1000 CAPTCHAs | Speed | Reliability |
|---------|------------------------|-------|-------------|
| **2captcha** | ~$2.99 | Fast | High |
| **AntiCaptcha** | ~$1.00 | Medium | High |
| **CapSolver** | Varies | Fast | High |
| **Local Solver** | **FREE** | Fast | Good (audio only) |

---

## Do You Actually Need It?

### ✅ **You DON'T need an API key if:**
- You're using the **local solver** (already working for audio CAPTCHAs)
- You're okay with manual solving for image challenges (`HEADLESS=false`)
- You're just testing/developing

### ❌ **You DO need an API key if:**
- You want **fully automated** image challenge solving
- You're running in production and can't solve manually
- You need 100% automation without any manual intervention

---

## Current Recommendation

**For now, stick with the FREE local solver:**
- ✅ Works for audio CAPTCHAs (most common)
- ✅ Fully automated
- ✅ No costs
- ✅ Already implemented and working

**Only get an API key if:**
- You frequently encounter image challenges
- You need 100% automation for image challenges
- You're running in production

---

## Testing Without API Key

You can test everything without an API key:

1. **For audio CAPTCHAs**: Local solver works (free)
2. **For image CAPTCHAs**: Use manual mode
   ```bash
   HEADLESS=false
   ```
   Then solve manually when image challenge appears.

---

## After Getting API Key

1. Add to `.env.local`:
   ```bash
   CAPTCHA_2CAPTCHA_API_KEY=your-key-here
   ```

2. Restart your Next.js server:
   ```bash
   npm run dev
   ```

3. The automation will automatically use it when needed

---

## Summary

- **Local solver**: FREE, works for audio ✅
- **Paid services**: ~$1-3 per 1000 CAPTCHAs, works for both audio and image
- **Manual solving**: FREE, works for everything (set `HEADLESS=false`)

**Recommendation**: Use local solver for now, only get API key if you need image challenge automation.

