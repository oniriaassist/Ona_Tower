$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

$Python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    throw "Virtual environment not found. Create it first with: python -m venv .venv"
}

& $Python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8400
