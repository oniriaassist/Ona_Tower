$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONPATH = "$Root\backend"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Virtual environment not found. Create it first with: python -m venv .venv"
}

& $Python -m pytest -c backend\pyproject.toml backend\tests -q
& $Python -m alembic -c database\alembic.ini current
Push-Location frontend
npm run check
Pop-Location
Write-Host "Verification complete."
