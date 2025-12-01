# TEQSmartSubmit Setup Script for Windows
Write-Host "Setting up TEQSmartSubmit..." -ForegroundColor Cyan

# Check Node.js
Write-Host "`nChecking Node.js..." -ForegroundColor Yellow
if (!(Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Node.js not found. Please install Node.js 18+ from https://nodejs.org" -ForegroundColor Red
    exit 1
}
$nodeVersion = node --version
Write-Host "[OK] Node.js $nodeVersion found" -ForegroundColor Green

# Check Python
Write-Host "`nChecking Python..." -ForegroundColor Yellow
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python not found. Please install Python 3.10+ from https://python.org" -ForegroundColor Red
    exit 1
}
$pythonVersion = python --version
Write-Host "[OK] $pythonVersion found" -ForegroundColor Green

# Install Node.js dependencies
Write-Host "`nInstalling Node.js dependencies..." -ForegroundColor Yellow
npm install --legacy-peer-deps
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install Node.js dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Node.js dependencies installed" -ForegroundColor Green

# Install Python dependencies
Write-Host "`nInstalling Python dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Failed to install Python dependencies" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Python dependencies installed" -ForegroundColor Green

# Install Playwright browsers
Write-Host "`nInstalling Playwright browsers..." -ForegroundColor Yellow
python -m playwright install chromium
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Playwright browser installation failed (optional)" -ForegroundColor Yellow
}

# Setup environment file
Write-Host "`nSetting up environment..." -ForegroundColor Yellow
if (!(Test-Path ".env.local")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env.local"
        Write-Host "[OK] Created .env.local from .env.example" -ForegroundColor Green
        Write-Host "[!] Please edit .env.local with your configuration" -ForegroundColor Yellow
    } else {
        Write-Host "[!] .env.example not found. Creating basic .env.local..." -ForegroundColor Yellow
        $envContent = @"
DATABASE_URL=postgresql://user:password@localhost:5432/teqsmartsubmit
GOOGLE_PLACES_API_KEY=your_key_here
VERCEL_TOKEN=your_token_here
GITHUB_TOKEN=your_token_here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
JWT_SECRET=change-this-secret-key-in-production
"@
        $envContent | Out-File -FilePath ".env.local" -Encoding utf8 -NoNewline
        Write-Host "[OK] Created basic .env.local" -ForegroundColor Green
    }
} else {
    Write-Host "[OK] .env.local already exists" -ForegroundColor Green
}

# Generate Prisma Client
Write-Host "`nGenerating Prisma Client..." -ForegroundColor Yellow
npx prisma generate
if ($LASTEXITCODE -ne 0) {
    Write-Host "[WARNING] Prisma generate failed. Make sure DATABASE_URL is set in .env.local" -ForegroundColor Yellow
}

Write-Host "`n[OK] Setup complete!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env.local with your configuration" -ForegroundColor White
Write-Host "2. Create PostgreSQL database: createdb teqsmartsubmit" -ForegroundColor White
Write-Host "3. Run migrations: npx prisma migrate dev" -ForegroundColor White
Write-Host "4. Start dev server: npm run dev" -ForegroundColor White
Write-Host "`nReady to run!" -ForegroundColor Green
