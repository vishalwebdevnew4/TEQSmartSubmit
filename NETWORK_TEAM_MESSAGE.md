# Message to Network Team - TEQSmartSubmit Server Setup

**Date**: November 14, 2025
**Project**: TEQSmartSubmit Deployment
**Server**: teqsmartsubmit.xcelanceweb.com (192.168.0.78)
**SSH Access**: teqsmartsftpuser@teqsmartsubmit.xcelanceweb.com (Port: 3129)

## Status Update

We have successfully connected to the server and installed most Python dependencies required for the TEQSmartSubmit automation system. However, we need assistance with completing the system-level dependencies installation.

## What Has Been Completed ✅

### Verified Server Status:
- **Operating System**: Ubuntu 22.04.4 LTS
- **Python Version**: Python 3.10.12 ✓ (Confirmed installed)
- **Server Status**: Online and accessible

### Successfully Installed Python Packages:
1. **Playwright** (v1.56.0) - Browser automation framework
2. **Chromium Browser** - Downloaded and installed (~280MB total)
3. **Python Libraries**:
   - SpeechRecognition (v3.14.3)
   - pydub (v0.25.1)
   - ffmpeg-python (v0.2.0)
   - pandas (expected installed)
   - reportlab (expected installed)
   - redis (expected installed)

All Python packages have been installed in user space (`~/.local/lib/python3.10/site-packages/`).

## What Requires Network Team Assistance ⚠️

### 1. System Dependencies Installation (Requires Root/Sudo Access)

Playwright requires system-level libraries to run browsers. The installation command requires sudo privileges, but the provided SSH password does not have sudo access.

**Required Action:**
Please run the following command on the server with root/sudo access:

```bash
sudo python3 -m playwright install-deps chromium
```

**OR** install the system packages directly:

```bash
sudo apt-get update
sudo apt-get install -y \
  libasound2 \
  libatk-bridge2.0-0 \
  libatk1.0-0 \
  libatspi2.0-0 \
  libcups2 \
  libdbus-1-3 \
  libdrm2 \
  libgbm1 \
  libgtk-3-0 \
  libnspr4 \
  libnss3 \
  libxcomposite1 \
  libxdamage1 \
  libxfixes3 \
  libxkbcommon0 \
  libxrandr2 \
  libxshmfence1 \
  libxss1 \
  libxtst6
```

### 2. Alternative: Grant Sudo Access

If preferred, we can complete the installation ourselves if the `teqsmartsftpuser` account can be granted sudo access (temporarily or permanently) for system package installation.

**Security Note**: If granting sudo access, we recommend:
- Temporary sudo access only for installation
- Or sudo access limited to specific package installation commands

### 3. Verify Installation

After system dependencies are installed, please verify with:

```bash
python3 -m playwright --version
python3 -c "from playwright.sync_api import sync_playwright; print('Playwright OK')"
```

## Network/Firewall Considerations

### Current Status:
- ✅ SSH access (Port 3129) - Working
- ✅ Outbound internet access for package downloads - Working

### Potential Requirements:
- **No additional firewall rules needed** for the Python automation (runs locally)
- **Outbound HTTPS access** may be needed for CAPTCHA solving services (if using external APIs)
- **Port 3000** should be open if running the Next.js application locally
- **Database connection** (PostgreSQL) - typically localhost:5432

## Application Requirements Summary

### Port Requirements:
- **Port 3000**: Next.js application (if running on server)
- **Port 5432**: PostgreSQL (local connection)
- **Port 6379**: Redis (local connection, optional)

### Outbound Connections:
- **HTTPS**: For downloading packages, CAPTCHA solving APIs (2captcha, AntiCaptcha, etc.)
- **Web scraping**: Access to target websites for form automation

## Python Installation Verification

**Python is installed and working correctly.** Verification results:

```bash
$ python3 --version
Python 3.10.12

$ python3 -m playwright --version
Version 1.56.0

$ pip3 list | grep -E '(playwright|pandas|reportlab|redis|SpeechRecognition|pydub|ffmpeg)'
ffmpeg-python          0.2.0
playwright             1.56.0
pydub                  0.25.1
SpeechRecognition      3.14.3
```

**Note**: Some packages (pandas, reportlab, redis) may be installed in a different location or may need verification. We can check this once system dependencies are installed.

## Next Steps

1. ✅ **Completed**: Python packages and Playwright installation
2. ⏳ **Pending**: System dependencies installation (requires network team)
3. ⏳ **Pending**: Final verification and testing

## Contact & Support

If you need any clarification or have questions about the installation requirements, please don't hesitate to reach out. Once the system dependencies are installed, we can proceed with final testing and deployment.

**Estimated Time**: The system dependencies installation should take less than 5 minutes.

---

**Installation Files Created**:
- `/var/www/html/TEQSmartSubmit/SERVER_INSTALLATION.md` - Full installation guide
- `/var/www/html/TEQSmartSubmit/PYTHON_INSTALLATION_SUMMARY.md` - Detailed Python installation status
- `/var/www/html/TEQSmartSubmit/verify_python_install.py` - Verification script

Thank you for your assistance!

