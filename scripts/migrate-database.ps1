$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
$env:PYTHONPATH = "$Root\backend"

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Virtual environment not found. Create it first with: python -m venv .venv"
}

& $Python -m alembic -c ".\database\alembic.ini" upgrade head
& $Python ".\seed.py"
& $Python ".\scripts\db_check.py"
