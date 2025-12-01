# Free AI Alternatives for Template Generation

Since OpenAI quota can be exceeded, here are **FREE alternatives** you can use:

## 🆓 Free Options

### 1. **Google Gemini** (Recommended - Easiest)
- **FREE Tier**: 60 requests/minute
- **Model**: `gemini-pro`
- **Quality**: Excellent, comparable to GPT-4
- **Setup**:
  1. Get free API key: https://makersuite.google.com/app/apikey
  2. Add to `.env` file:
     ```
     GOOGLE_AI_API_KEY=your_key_here
     ```
  3. Install package:
     ```bash
     pip install google-generativeai
     ```

### 2. **Hugging Face Inference API**
- **FREE Tier**: Available (rate limits apply)
- **Model**: `mistralai/Mistral-7B-Instruct-v0.2`
- **Quality**: Good for code generation
- **Setup**:
  1. Create account: https://huggingface.co/join
  2. Get free token: https://huggingface.co/settings/tokens
  3. Add to `.env` file:
     ```
     HUGGINGFACE_API_KEY=your_token_here
     ```
  4. Package already installed (`requests`)

## 🎯 Priority Order

The system tries AI services in this order:
1. **OpenAI** (if quota available)
2. **Google Gemini** (FREE) ⭐ Recommended
3. **Hugging Face** (FREE)
4. **Anthropic** (if available)
5. **Fallback Template** (always works)

## 📝 Quick Setup

### For Google Gemini (Easiest):
```bash
# 1. Install
pip install google-generativeai

# 2. Get API key from: https://makersuite.google.com/app/apikey

# 3. Add to .env file
echo "GOOGLE_AI_API_KEY=your_key_here" >> .env
```

### For Hugging Face:
```bash
# 1. Get token from: https://huggingface.co/settings/tokens

# 2. Add to .env file
echo "HUGGINGFACE_API_KEY=your_token_here" >> .env
```

## ✅ Verification

After adding your API key, generate a website. You should see:
- `[AI] Using Google Gemini...` in console
- Or `[AI] Using Hugging Face...` in console
- **✨ GPT Generated** badge (even though it's Gemini/HF)

## 💡 Tips

- **Google Gemini** is the easiest and most reliable free option
- Both services have rate limits, but are generous for free tier
- The system automatically falls back if one service fails
- You can use multiple services - it tries them in order

## 🔗 Links

- Google Gemini API: https://makersuite.google.com/app/apikey
- Hugging Face Tokens: https://huggingface.co/settings/tokens
- Hugging Face Models: https://huggingface.co/models

