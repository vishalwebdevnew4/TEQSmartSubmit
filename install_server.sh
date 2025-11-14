#!/bin/bash
# TEQSmartSubmit Remote Server Installation Script
# This script automates the installation of system dependencies

set -e  # Exit on error

echo "=========================================="
echo "TEQSmartSubmit Server Installation Script"
echo "=========================================="
echo ""

# Check if running as root for system packages
if [ "$EUID" -eq 0 ]; then 
   echo "Warning: Running as root. Some commands may need sudo."
   SUDO=""
else
   SUDO="sudo"
   echo "Note: This script will use sudo for system package installation."
fi

# Update system packages
echo "[1/10] Updating system packages..."
$SUDO apt update && $SUDO apt upgrade -y

# Install Node.js (if not already installed)
if ! command -v node &> /dev/null; then
    echo "[2/10] Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_18.x | $SUDO -E bash -
    $SUDO apt-get install -y nodejs
else
    echo "[2/10] Node.js already installed: $(node --version)"
fi

# Install Python and pip (if not already installed)
if ! command -v python3 &> /dev/null; then
    echo "[3/10] Installing Python 3..."
    $SUDO apt-get install -y python3 python3-pip python3-venv
else
    echo "[3/10] Python already installed: $(python3 --version)"
fi

# Install PostgreSQL (if not already installed)
if ! command -v psql &> /dev/null; then
    echo "[4/10] Installing PostgreSQL..."
    $SUDO apt-get install -y postgresql postgresql-contrib
else
    echo "[4/10] PostgreSQL already installed"
fi

# Install Git (if not already installed)
if ! command -v git &> /dev/null; then
    echo "[5/10] Installing Git..."
    $SUDO apt-get install -y git
else
    echo "[5/10] Git already installed: $(git --version)"
fi

# Install build tools
echo "[6/10] Installing build tools..."
$SUDO apt-get install -y build-essential

# Install FFmpeg (for CAPTCHA solver audio processing)
echo "[7/10] Installing FFmpeg..."
$SUDO apt-get install -y ffmpeg

# Install Redis (optional but recommended)
echo "[8/10] Installing Redis..."
$SUDO apt-get install -y redis-server
$SUDO systemctl enable redis-server || true

# Install Playwright system dependencies
echo "[9/10] Installing Playwright system dependencies..."
if command -v pip3 &> /dev/null; then
    pip3 install --user playwright || $SUDO pip3 install playwright
    # Install Playwright browsers (requires user interaction if not in PATH)
    python3 -m playwright install chromium || echo "Warning: Could not install Playwright browsers. Run 'playwright install chromium' manually."
    python3 -m playwright install-deps chromium || echo "Warning: Could not install Playwright system dependencies. Run 'playwright install-deps chromium' manually."
else
    echo "Warning: pip3 not found. Skipping Playwright installation."
    echo "Install Playwright manually: pip3 install playwright && playwright install chromium"
fi

# Summary
echo ""
echo "[10/10] Installation Summary"
echo "=========================================="
echo "Node.js: $(node --version 2>/dev/null || echo 'Not installed')"
echo "npm: $(npm --version 2>/dev/null || echo 'Not installed')"
echo "Python: $(python3 --version 2>/dev/null || echo 'Not installed')"
echo "PostgreSQL: $(psql --version 2>/dev/null || echo 'Not installed')"
echo "Git: $(git --version 2>/dev/null || echo 'Not installed')"
echo "FFmpeg: $(ffmpeg -version 2>/dev/null | head -n1 || echo 'Not installed')"
echo "Redis: $(redis-cli --version 2>/dev/null || echo 'Not installed')"
echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "1. Create PostgreSQL database and user:"
echo "   sudo -u postgres psql"
echo "   CREATE DATABASE teqsmartsubmit;"
echo "   CREATE USER teqsmartuser WITH PASSWORD 'your_password';"
echo "   GRANT ALL PRIVILEGES ON DATABASE teqsmartsubmit TO teqsmartuser;"
echo ""
echo "2. Install application dependencies:"
echo "   npm install"
echo "   npx prisma generate"
echo ""
echo "3. Setup database schema:"
echo "   npx prisma db push"
echo ""
echo "4. Create .env.local file with required variables:"
echo "   DATABASE_URL=postgresql://teqsmartuser:password@localhost:5432/teqsmartsubmit"
echo "   AUTH_JWT_SECRET=your-secret-key"
echo "   TEQ_ADMIN_REGISTRATION_TOKEN=your-admin-token"
echo ""
echo "5. Build and start application:"
echo "   npm run build"
echo "   npm start"
echo ""
echo "For detailed instructions, see: SERVER_INSTALLATION.md"
echo ""

