# Remote Server Installation Guide

This guide covers all dependencies and setup steps required to deploy TEQSmartSubmit on a remote server.

## System Requirements

- **OS**: Linux (Ubuntu 20.04+ recommended) or compatible distribution
- **Memory**: Minimum 2GB RAM (4GB+ recommended for automation)
- **Disk**: Minimum 10GB free space

## Step 1: System Package Installation

### Update System Packages
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Core Dependencies
```bash
# Node.js 18+ and npm
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python 3.8+ and pip
sudo apt-get install -y python3 python3-pip python3-venv

# PostgreSQL Database
sudo apt-get install -y postgresql postgresql-contrib

# Git (if not already installed)
sudo apt-get install -y git

# Build tools (required for some npm packages)
sudo apt-get install -y build-essential

# FFmpeg (required for local CAPTCHA solver audio processing)
sudo apt-get install -y ffmpeg

# Redis (optional, but recommended for caching/queue management)
sudo apt-get install -y redis-server
```

### Verify Installations
```bash
node --version  # Should be v18.x or higher
npm --version
python3 --version  # Should be 3.8+
psql --version
redis-cli --version
```

## Step 2: Python Environment Setup

### Option A: Using Poetry (Recommended for Backend)

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Add Poetry to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Verify Poetry installation
poetry --version
```

### Option B: Using pip (Simpler, for automation scripts only)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

## Step 3: Database Setup

### Create PostgreSQL Database and User

```bash
# Switch to postgres user
sudo -u postgres psql

# In PostgreSQL prompt, run:
CREATE DATABASE teqsmartsubmit;
CREATE USER teqsmartuser WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE teqsmartsubmit TO teqsmartuser;
\q
```

### Configure PostgreSQL (Optional - for remote access)

Edit `/etc/postgresql/*/main/postgresql.conf`:
```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
# Uncomment: listen_addresses = 'localhost'
```

Edit `/etc/postgresql/*/main/pg_hba.conf`:
```bash
sudo nano /etc/postgresql/*/main/pg_hba.conf
# Add: host    teqsmartsubmit    teqsmartuser    127.0.0.1/32    md5
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## Step 4: Application Setup

### Clone/Navigate to Project Directory
```bash
cd /var/www/html/TEQSmartSubmit
# Or if cloning:
# git clone <your-repo-url> /var/www/html/TEQSmartSubmit
# cd /var/www/html/TEQSmartSubmit
```

### Install Node.js Dependencies

```bash
npm install
```

### Generate Prisma Client

```bash
npx prisma generate
```

### Setup Database Schema

```bash
# Push schema to database
npx prisma db push

# Or run migrations (if using migrations)
# npx prisma migrate dev --name init
```

### Seed Database (Optional)

```bash
npm run db:seed
```

## Step 5: Python Dependencies

### Install Automation Script Dependencies

**Option A: Using pip (Recommended for automation scripts)**
```bash
# Install Playwright and browsers
pip3 install playwright
playwright install chromium
playwright install-deps chromium

# Install automation dependencies
pip3 install playwright pandas reportlab redis
```

**Option B: Using Poetry (For backend)**
```bash
cd backend
poetry install
poetry run playwright install chromium
poetry run playwright install-deps chromium
```

### Install CAPTCHA Solver Dependencies (Optional)

If using the local CAPTCHA solver:
```bash
pip3 install SpeechRecognition pydub ffmpeg-python
```

## Step 6: Environment Configuration

### Create Environment File

```bash
# Copy example if exists, or create new
nano .env.local
```

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://teqsmartuser:your_secure_password_here@localhost:5432/teqsmartsubmit

# API Configuration
NEXT_PUBLIC_API_BASE_URL=/api
TEQ_ADMIN_REGISTRATION_TOKEN=your-secure-admin-token-here

# Authentication
AUTH_JWT_SECRET=your-very-secure-random-secret-key-here
AUTH_JWT_EXPIRES=1h

# Playwright (Optional)
HEADLESS=true

# CAPTCHA Solving (Optional - choose one)
# For 2captcha:
# CAPTCHA_2CAPTCHA_API_KEY=your-2captcha-api-key
# For AntiCaptcha:
# CAPTCHA_ANTICAPTCHA_API_KEY=your-anticaptcha-api-key
# For CapSolver:
# CAPTCHA_CAPSOLVER_API_KEY=your-capsolver-api-key
# For Local Solver:
# TEQ_USE_LOCAL_CAPTCHA_SOLVER=true

# Redis (Optional)
REDIS_URL=redis://localhost:6379
```

### Generate Secure Secrets

```bash
# Generate JWT secret
openssl rand -base64 32

# Generate admin token
openssl rand -hex 16
```

## Step 7: Build and Start Application

### Production Build

```bash
# Build Next.js application
npm run build
```

### Start Application

**Option A: Using PM2 (Recommended for production)**
```bash
# Install PM2 globally
sudo npm install -g pm2

# Start application
pm2 start npm --name "teqsmartsubmit" -- start

# Save PM2 configuration
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Follow the instructions printed by the command
```

**Option B: Using systemd**

Create `/etc/systemd/system/teqsmartsubmit.service`:
```ini
[Unit]
Description=TEQSmartSubmit Next.js Application
After=network.target postgresql.service redis.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/html/TEQSmartSubmit
Environment=NODE_ENV=production
EnvironmentFile=/var/www/html/TEQSmartSubmit/.env.local
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable teqsmartsubmit
sudo systemctl start teqsmartsubmit
sudo systemctl status teqsmartsubmit
```

**Option C: Using Nginx as Reverse Proxy**

Install Nginx:
```bash
sudo apt-get install -y nginx
```

Create `/etc/nginx/sites-available/teqsmartsubmit`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/teqsmartsubmit /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

For HTTPS with Let's Encrypt:
```bash
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Step 8: Verify Installation

### Check Services

```bash
# Check PostgreSQL
sudo systemctl status postgresql

# Check Redis (if installed)
sudo systemctl status redis-server

# Check application
pm2 status
# or
sudo systemctl status teqsmartsubmit
```

### Test Application

```bash
# Check if application is running
curl http://localhost:3000/api/health

# Access via browser
# http://your-server-ip:3000 or http://your-domain.com
```

## Step 9: Firewall Configuration

```bash
# Allow SSH (important!)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow application port (if not using reverse proxy)
sudo ufw allow 3000/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

## Step 10: Maintenance Commands

### Update Application

```bash
cd /var/www/html/TEQSmartSubmit
git pull
npm install
npx prisma generate
npm run build
pm2 restart teqsmartsubmit
# or
sudo systemctl restart teqsmartsubmit
```

### View Logs

```bash
# PM2 logs
pm2 logs teqsmartsubmit

# systemd logs
sudo journalctl -u teqsmartsubmit -f

# Application logs (if configured)
tail -f /var/log/teqsmartsubmit.log
```

### Database Backup

```bash
# Backup database
pg_dump -U teqsmartuser teqsmartsubmit > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore database
psql -U teqsmartuser teqsmartsubmit < backup_file.sql
```

## Troubleshooting

### Common Issues

1. **Playwright browser not found**
   ```bash
   playwright install chromium
   playwright install-deps chromium
   ```

2. **Permission denied errors**
   ```bash
   sudo chown -R $USER:$USER /var/www/html/TEQSmartSubmit
   ```

3. **Database connection errors**
   - Verify PostgreSQL is running: `sudo systemctl status postgresql`
   - Check DATABASE_URL in .env.local
   - Verify database user permissions

4. **Port already in use**
   ```bash
   # Find process using port 3000
   sudo lsof -i :3000
   # Kill process if needed
   sudo kill -9 <PID>
   ```

5. **Memory issues with automation**
   - Ensure sufficient swap space
   - Consider increasing server RAM
   - Limit concurrent automation runs

## Additional Security Recommendations

1. **Keep system updated**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Use strong passwords** for database and admin tokens

3. **Configure fail2ban** to protect against brute force attacks
   ```bash
   sudo apt-get install -y fail2ban
   ```

4. **Regular backups** of database and configuration files

5. **Monitor logs** for suspicious activity

6. **Use HTTPS** in production (via Let's Encrypt)

## Quick Reference Checklist

- [ ] Node.js 18+ installed
- [ ] Python 3.8+ installed
- [ ] PostgreSQL installed and database created
- [ ] Redis installed (optional)
- [ ] FFmpeg installed (if using local CAPTCHA solver)
- [ ] Application dependencies installed (npm install)
- [ ] Prisma client generated
- [ ] Database schema pushed
- [ ] Playwright browsers installed
- [ ] Environment variables configured
- [ ] Application built and running
- [ ] Firewall configured
- [ ] Domain/SSL configured (if applicable)

