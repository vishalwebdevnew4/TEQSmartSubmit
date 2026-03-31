# CAPTCHA Solver System

A flexible, extensible CAPTCHA solving system that supports multiple providers and can be extended with custom solvers.

## 🎯 Supported Services

### 1. **2captcha** (Default)
- **Cost**: ~$2.99 per 1000 reCAPTCHA v2 solves
- **Setup**: Set `CAPTCHA_2CAPTCHA_API_KEY` or `TEQ_CAPTCHA_API_KEY`
- **Website**: https://2captcha.com

### 2. **AntiCaptcha**
- **Cost**: Competitive pricing
- **Setup**: Set `CAPTCHA_ANTICAPTCHA_API_KEY`
- **Website**: https://anti-captcha.com

### 3. **CapSolver**
- **Cost**: Competitive pricing
- **Setup**: Set `CAPTCHA_CAPSOLVER_API_KEY`
- **Website**: https://capsolver.com

### 4. **Local Solver** (Placeholder)
- **Status**: Framework ready, implementation needed
- **Use Case**: Custom ML models, self-hosted solutions

## 🚀 Quick Start

### Option 1: Auto-Detection (Recommended)
The system automatically detects which service to use based on available API keys:

```bash
# In .env.local
CAPTCHA_2CAPTCHA_API_KEY=your-api-key-here
```

### Option 2: Specify Service
Explicitly choose a service in your template:

```json
{
  "captcha_service": "2captcha",
  "fields": [...],
  ...
}
```

## 📝 Configuration

### Environment Variables

```bash
# 2captcha (default)
CAPTCHA_2CAPTCHA_API_KEY=your-key
TEQ_CAPTCHA_API_KEY=your-key  # Alternative name

# AntiCaptcha
CAPTCHA_ANTICAPTCHA_API_KEY=your-key

# CapSolver
CAPTCHA_CAPSOLVER_API_KEY=your-key
```

### Template Configuration

```json
{
  "captcha_service": "2captcha",  // or "anticaptcha", "capsolver", "auto"
  "captcha_api_key": "optional-override-key",
  "headless": false,  // For manual solving
  ...
}
```

## 🔧 Architecture

### Base Class: `CaptchaSolver`
All solvers inherit from this base class:

```python
class CaptchaSolver:
    async def solve_recaptcha_v2(site_key, page_url) -> str
    async def solve_hcaptcha(site_key, page_url) -> str
```

### Service Implementations
- `TwoCaptchaSolver` - 2captcha.com integration
- `AntiCaptchaSolver` - AntiCaptcha.com integration
- `CapSolverSolver` - CapSolver.com integration
- `LocalCaptchaSolver` - Placeholder for custom implementation

## 🛠️ Creating a Custom Solver

### Example: Custom CAPTCHA Solver

```python
from automation.captcha_solver import CaptchaSolver

class MyCustomSolver(CaptchaSolver):
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def solve_recaptcha_v2(self, site_key: str, page_url: str) -> Optional[str]:
        # Your custom solving logic here
        # Return the solved token
        return solved_token
    
    async def solve_hcaptcha(self, site_key: str, page_url: str) -> Optional[str]:
        # Your custom solving logic here
        return solved_token
```

### Register Your Solver

Update `get_captcha_solver()` in `automation/captcha_solver.py`:

```python
def get_captcha_solver(service: str = "auto") -> Optional[CaptchaSolver]:
    if service == "mycustom":
        api_key = os.getenv("MY_CUSTOM_API_KEY")
        if api_key:
            return MyCustomSolver(api_key)
    # ... existing code
```

## 🧪 Testing

### Test with Manual Solving (Free)
```bash
# Set in template or environment
HEADLESS=false
```

### Test with Automatic Solving
```bash
# Set API key
export CAPTCHA_2CAPTCHA_API_KEY=your-key

# Run automation
python3 automation/run_submission.py --url ... --template ...
```

## 📊 Service Comparison

| Service | reCAPTCHA v2 | hCaptcha | Speed | Reliability |
|---------|--------------|----------|-------|-------------|
| 2captcha | ✅ | ✅ | Medium | High |
| AntiCaptcha | ✅ | ✅ | Fast | High |
| CapSolver | ✅ | ✅ | Fast | High |
| Local | ⚠️ | ⚠️ | Fast | Depends |

## 🔐 Security Notes

- **Never commit API keys** to version control
- Use environment variables or secure secret management
- Rotate API keys regularly
- Monitor usage to detect abuse

## 💡 Tips

1. **Development**: Use `HEADLESS=false` for manual solving (free)
2. **Production**: Use automatic solving with API key
3. **Cost Optimization**: Compare prices across services
4. **Reliability**: Have a fallback service configured
5. **Monitoring**: Track success rates per service

## 🐛 Troubleshooting

### "No CAPTCHA solver configured"
- Set at least one API key environment variable
- Or set `HEADLESS=false` for manual solving

### "Solver returned empty token"
- Check API key is valid
- Verify account has sufficient balance
- Check service status/availability

### "Timeout waiting for solution"
- Increase timeout in template: `captcha_timeout_ms: 120000`
- Check service response times
- Verify network connectivity

## 📚 API Documentation

### 2captcha
- Docs: https://2captcha.com/2captcha-api

### AntiCaptcha
- Docs: https://anticaptcha.atlassian.net/wiki/spaces/API

### CapSolver
- Docs: https://docs.capsolver.com/

## 🎓 Building a Local Solver

To build your own local CAPTCHA solver, you'll need:

1. **Image Recognition**: For image-based CAPTCHAs
   - Libraries: OpenCV, PIL, TensorFlow
   - Models: Trained on CAPTCHA datasets

2. **Audio Recognition**: For audio CAPTCHAs
   - Libraries: SpeechRecognition, pydub
   - Services: Google Speech-to-Text, Azure

3. **ML Models**: For pattern recognition
   - Frameworks: TensorFlow, PyTorch
   - Training: Large datasets of solved CAPTCHAs

4. **Browser Automation**: To interact with CAPTCHA
   - Playwright (already integrated)
   - Selenium alternatives

**Note**: Building a reliable local solver is complex and may violate terms of service. Use at your own risk.

## 🔄 Future Enhancements

- [ ] Support for reCAPTCHA v3
- [ ] Support for FunCaptcha
- [ ] Support for GeeTest
- [ ] Local ML-based solver implementation
- [ ] Solver performance metrics
- [ ] Automatic failover between services
- [ ] Cost tracking per service

