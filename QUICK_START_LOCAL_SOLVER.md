# Quick Start: Local CAPTCHA Solver

## ✅ Fully Automated - No Manual Intervention Needed!

## 🚀 Setup (One-Time)

```bash
# 1. Install Python dependencies
pip install SpeechRecognition pydub

# 2. Install system dependency (if not already installed)
sudo apt-get install ffmpeg  # Ubuntu/Debian
# or
brew install ffmpeg          # macOS
```

## ⚙️ Enable Local Solver

### Method 1: Environment Variable (Recommended)
```bash
# Add to .env.local
TEQ_USE_LOCAL_CAPTCHA_SOLVER=true
```

### Method 2: Template Configuration
```json
{
  "use_local_captcha_solver": true,
  "url": "https://example.com",
  "fields": [...],
  ...
}
```

## 🎯 That's It!

Now when you run automation:
- ✅ CAPTCHA detected automatically
- ✅ Checkbox clicked automatically  
- ✅ Audio challenges solved automatically (if they appear)
- ✅ Token extracted and injected automatically
- ✅ Form submits automatically

**No manual intervention needed!**

## 🧪 Test It

```bash
# Test via API
curl -X POST http://localhost:3000/api/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://interiordesign.xcelanceweb.com/",
    "template": {
      "use_local_captcha_solver": true,
      "fields": [...],
      ...
    }
  }'
```

## 📊 How It Works

1. **Detects CAPTCHA** - Finds reCAPTCHA on the page
2. **Clicks Checkbox** - Automatically clicks the reCAPTCHA checkbox
3. **Handles Challenges** - If audio challenge appears:
   - Clicks audio button
   - Downloads audio file
   - Converts to text using speech recognition
   - Enters text and verifies
4. **Extracts Token** - Gets the solved token
5. **Injects Token** - Puts token in the form
6. **Submits Form** - Continues with submission

## ⚠️ Troubleshooting

**"speech_recognition not found"**
```bash
pip install SpeechRecognition pydub
```

**"ffmpeg not found"**
```bash
sudo apt-get install ffmpeg
```

**CAPTCHA not solving?**
- Check browser console for errors
- Verify CAPTCHA is actually present
- Try with `headless: false` to see what's happening

## 🎉 Success!

Your automation now solves CAPTCHAs automatically without any paid services or manual intervention!

