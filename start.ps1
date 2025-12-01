# TEQSmartSubmit Startup Script for Windows
Write-Host "Starting TEQSmartSubmit..." -ForegroundColor Cyan

# Check if .env.local exists
if (!(Test-Path ".env.local")) {
    Write-Host "[ERROR] .env.local not found. Please run setup.ps1 first" -ForegroundColor Red
    exit 1
}

# Check if database is configured
$envContent = Get-Content ".env.local" -Raw
if ($envContent -notmatch "DATABASE_URL") {
    Write-Host "[WARNING] DATABASE_URL not found in .env.local" -ForegroundColor Yellow
}

# Start Next.js dev server
Write-Host "`nStarting Next.js development server..." -ForegroundColor Yellow
Write-Host "Server will be available at http://localhost:3000" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server`n" -ForegroundColor Gray

npm run dev

