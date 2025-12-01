# Restart Next.js Dev Server with Cache Clear
Write-Host "`n=== RESTARTING DEV SERVER ===" -ForegroundColor Cyan

# Stop any running Node processes on port 3000
Write-Host "`n1. Stopping existing dev servers..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
foreach ($pid in $processes) {
    try {
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        Write-Host "  ✓ Stopped process $pid" -ForegroundColor Green
    } catch {
        Write-Host "  ℹ Process $pid already stopped" -ForegroundColor Gray
    }
}
Start-Sleep -Seconds 2

# Clear Next.js cache
Write-Host "`n2. Clearing Next.js cache..." -ForegroundColor Yellow
if (Test-Path ".next") {
    Remove-Item -Recurse -Force ".next" -ErrorAction SilentlyContinue
    Write-Host "  ✓ Cleared .next cache" -ForegroundColor Green
}
if (Test-Path "node_modules/.cache") {
    Remove-Item -Recurse -Force "node_modules/.cache" -ErrorAction SilentlyContinue
    Write-Host "  ✓ Cleared node_modules cache" -ForegroundColor Green
}

# Verify routes exist
Write-Host "`n3. Verifying routes..." -ForegroundColor Yellow
$routes = @(
    "src/app/page.tsx",
    "src/app/login/page.tsx",
    "src/app/test/page.tsx",
    "src/app/layout.tsx"
)
$allExist = $true
foreach ($route in $routes) {
    if (Test-Path $route) {
        Write-Host "  ✓ $route" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $route MISSING!" -ForegroundColor Red
        $allExist = $false
    }
}

if (-not $allExist) {
    Write-Host "`n❌ Some routes are missing! Fix them before starting." -ForegroundColor Red
    exit 1
}

# Start dev server
Write-Host "`n4. Starting dev server..." -ForegroundColor Yellow
Write-Host "  Running: npm run dev" -ForegroundColor Gray
Write-Host "`n=== SERVER STARTING ===" -ForegroundColor Cyan
Write-Host "Wait for 'Ready' message, then test:" -ForegroundColor Yellow
Write-Host "  - http://localhost:3000/test" -ForegroundColor Cyan
Write-Host "  - http://localhost:3000/login" -ForegroundColor Cyan
Write-Host "`nPress Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "`n" -NoNewline

npm run dev

