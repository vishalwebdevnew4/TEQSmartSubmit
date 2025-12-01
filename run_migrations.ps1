# PowerShell script to run database migrations

Write-Host "Running database migrations..." -ForegroundColor Cyan

Set-Location backend

# Try python -m alembic first, then try alembic directly
if (Get-Command python -ErrorAction SilentlyContinue) {
    python -m alembic upgrade head
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Migration failed" -ForegroundColor Red
        Set-Location ..
        exit 1
    }
} else {
    Write-Host "❌ Python not found in PATH" -ForegroundColor Red
    Set-Location ..
    exit 1
}

Set-Location ..

Write-Host "✓ Migrations completed successfully" -ForegroundColor Green

