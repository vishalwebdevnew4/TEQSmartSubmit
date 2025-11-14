# Quick Installation Guide for Remote Server

## One-Command System Setup

```bash
# Run the automated installation script
bash install_server.sh
```

Or manually run these essential commands:

## Essential Installation Commands

### 1. System Packages
```bash
sudo apt update && sudo apt upgrade -y
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs python3 python3-pip postgresql postgresql-contrib git build-essential ffmpeg redis-server
```

### 2. Python Dependencies
```bash
pip3 install playwright
python3 -m playwright install chromium
python3 -m playwright install-deps chromium
```

### 3. Database Setup
```bash
sudo -u postgres psql
```
Then in PostgreSQL:
```sql
CREATE DATABASE teqsmartsubmit;
CREATE USER teqsmartuser WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE teqsmartsubmit TO teqsmartuser;
\q
```

### 4. Application Setup
```bash
cd /var/www/html/TEQSmartSubmit
npm install
npx prisma generate
npx prisma db push
npm run build
```

### 5. Environment Configuration
Create `.env.local`:
```bash
DATABASE_URL=postgresql://teqsmartuser:your_password@localhost:5432/teqsmartsubmit
AUTH_JWT_SECRET=$(openssl rand -base64 32)
TEQ_ADMIN_REGISTRATION_TOKEN=$(openssl rand -hex 16)
NEXT_PUBLIC_API_BASE_URL=/api
```

### 6. Start Application
```bash
# Option 1: Direct start
npm start

# Option 2: With PM2 (recommended for production)
npm install -g pm2
pm2 start npm --name "teqsmartsubmit" -- start
pm2 save
pm2 startup  # Follow instructions
```

## Minimum Required Packages

**System:**
- Node.js 18+
- Python 3.8+
- PostgreSQL
- FFmpeg (for CAPTCHA solver)
- Build tools

**Application:**
- npm packages (via `npm install`)
- Playwright browsers (via `playwright install chromium`)
- Prisma client (via `npx prisma generate`)

## Verification

Check all services:
```bash
node --version    # Should be v18.x+
python3 --version # Should be 3.8+
psql --version    # PostgreSQL installed
redis-cli ping    # Should return PONG
```

## Full Documentation

See `SERVER_INSTALLATION.md` for complete detailed instructions.

