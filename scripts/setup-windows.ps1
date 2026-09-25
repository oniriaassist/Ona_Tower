$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "ONA Towers dependency setup" -ForegroundColor Cyan

if (-not (Test-Path ".venv")) {
    py -3.13 -m venv .venv
}

& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\python.exe" -m pip install -r ".\requirements.txt"

Push-Location ".\frontend"
npm ci
Pop-Location

& ".\scripts\configure-local.ps1"

Write-Host ""
Write-Host "Setup complete. Database migrations were NOT run automatically." -ForegroundColor Green
Write-Host "Next: python scripts\doctor.py"
Write-Host "Then: .\scripts\migrate-database.ps1"
