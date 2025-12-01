# Fix Next.js Route Detection Issue
# This script downgrades Next.js to a more stable version

Write-Host ""
Write-Host "=== FIXING NEXT.JS ROUTE DETECTION ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "The issue: Next.js 15.0.3 might have route detection bugs" -ForegroundColor Yellow
Write-Host "Solution: Downgrade to Next.js 14 (more stable)" -ForegroundColor Green
Write-Host ""

Write-Host "1. Stopping dev server..." -ForegroundColor Yellow
Get-Process | Where-Object { $_.ProcessName -eq "node" } | Where-Object { 
    $_.Path -like "*TEQSmartSubmit*" -or (Get-NetTCPConnection -OwningProcess $_.Id -LocalPort 3000 -ErrorAction SilentlyContinue)
} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "2. Backing up package.json..." -ForegroundColor Yellow
Copy-Item "package.json" "package.json.backup" -Force
Write-Host "  Backed up" -ForegroundColor Green

Write-Host ""
Write-Host "3. Updating package.json to use Next.js 14..." -ForegroundColor Yellow
$packageContent = Get-Content "package.json" -Raw
$packageJson = $packageContent | ConvertFrom-Json
$packageJson.dependencies.next = "^14.2.0"
$packageJson.dependencies.react = "^18.3.0"
if ($packageJson.dependencies.'react-dom') {
    $packageJson.dependencies.'react-dom' = "^18.3.0"
} else {
    $packageJson.dependencies | Add-Member -MemberType NoteProperty -Name "react-dom" -Value "^18.3.0" -Force
}
$packageJson | ConvertTo-Json -Depth 10 | Set-Content "package.json"
Write-Host "  Updated package.json" -ForegroundColor Green

Write-Host ""
Write-Host "4. Removing node_modules and lock file..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    Remove-Item -Recurse -Force "node_modules" -ErrorAction SilentlyContinue
    Write-Host "  Removed node_modules" -ForegroundColor Green
}
if (Test-Path "package-lock.json") {
    Remove-Item -Force "package-lock.json" -ErrorAction SilentlyContinue
    Write-Host "  Removed package-lock.json" -ForegroundColor Green
}

Write-Host ""
Write-Host "5. Installing Next.js 14..." -ForegroundColor Yellow
Write-Host "  This may take a few minutes..." -ForegroundColor Gray
npm install --legacy-peer-deps

Write-Host ""
Write-Host "6. Clearing Next.js cache..." -ForegroundColor Yellow
if (Test-Path ".next") {
    Remove-Item -Recurse -Force ".next" -ErrorAction SilentlyContinue
    Write-Host "  Cleared cache" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host ""
Write-Host "Now try: npm run dev" -ForegroundColor Cyan
Write-Host "Then test: http://localhost:3000/login" -ForegroundColor Cyan
Write-Host ""
Write-Host "If you want to revert, restore package.json.backup" -ForegroundColor Yellow
