param(
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

Write-Host "ONA Towers local configuration" -ForegroundColor Cyan

if ((Test-Path ".env") -and -not $Force) {
    Write-Host "[ OK ] .env already exists. It was not overwritten." -ForegroundColor Green
} else {
    Copy-Item ".env.example" ".env" -Force
    Write-Host "[ OK ] Created .env from .env.example" -ForegroundColor Green
}

Write-Host ""
Write-Host "Local defaults:" -ForegroundColor Cyan
Write-Host "  Database : SQLite -> database/ona_towers.db"
Write-Host "  Backend  : http://127.0.0.1:8400"
Write-Host "  Frontend : http://127.0.0.1:3010"
Write-Host "  API path : /api"
Write-Host ""
Write-Host "For normal local development you do not need PostgreSQL or Supabase." -ForegroundColor Yellow
Write-Host "For production/Supabase, replace DATABASE_URL and MIGRATION_DATABASE_URL in .env with the exact Supabase connection strings." -ForegroundColor Yellow
Write-Host "Never commit .env or real credentials." -ForegroundColor Yellow
