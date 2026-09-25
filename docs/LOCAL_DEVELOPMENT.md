# ONA Towers — Local Development Guide (Windows)

This guide shows the complete local setup step by step instead of hiding it behind one setup command.

The ONA Towers ports are unchanged:

- Vite/React frontend: **3010**
- FastAPI backend: **8400**

## Requirements

Install:

- Python 3.13
- Node.js 22 + npm
- Git (recommended)
- VS Code (recommended)

Open PowerShell in the repository root (`ONA_Tower/`).

## 1. Create and activate `.venv`

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `Activate.ps1` is blocked:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

## 2. Create the local environment file

```powershell
.\scripts\configure-local.ps1
```

This safely creates `.env` from `.env.example`. It will not overwrite an existing `.env` unless you explicitly run:

```powershell
.\scripts\configure-local.ps1 -Force
```

The normal local database is SQLite at `database/ona_towers.db`, so no separate PostgreSQL service is required.

## 3. Install React/Vite dependencies

```powershell
cd frontend
npm ci
cd ..
```

The repository includes `frontend/package-lock.json`, so `npm ci` is the reproducible installation command.

## 4. Run the environment doctor

```powershell
python scripts\doctor.py
```

Do not continue to migrations until the checks pass. The final line should be:

```text
ALL LOCAL PREREQUISITE CHECKS PASSED
```

For the default local database you should also see:

```text
[ OK ] SQLite connection and authentication work.
```

## 5. Apply Alembic migrations

```powershell
python -m alembic -c database\alembic.ini upgrade head
```

Check the revision:

```powershell
python -m alembic -c database\alembic.ini current
```

Expected head:

```text
c4f2a31b7d90 (head)
```

## 6. Seed and validate ONA data

```powershell
python seed.py
python scripts\db_check.py
```

Then run backend tests:

```powershell
python -m pytest -c backend\pyproject.toml backend\tests -q
```

A convenience command combining migration, seed and database check is also available:

```powershell
.\scripts\migrate-database.ps1
```

## 7. Start FastAPI

Terminal 1:

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\start-backend.ps1
```

Direct command without the helper:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8400
```

Verify:

- `http://127.0.0.1:8400/health`
- `http://127.0.0.1:8400/docs`
- `http://127.0.0.1:8400/api/residences`

## 8. Start Vite/React

Terminal 2:

```powershell
.\scripts\start-frontend.ps1
```

Open:

- Public site: `http://127.0.0.1:3010`
- Admin: `http://127.0.0.1:3010/admin`

The frontend proxies `/api` and `/health` to the backend at `http://127.0.0.1:8400`.

## 9. Smoke-test the live full stack

Terminal 3, while both servers remain running:

```powershell
.\scripts\smoke-test.ps1
```

Successful output ends with:

```text
ALL LOCAL CHECKS PASSED
```

## 10. Daily startup after first setup

You do not reinstall dependencies or recreate the database every day.

Terminal 1:

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\start-backend.ps1
```

Terminal 2:

```powershell
.\scripts\start-frontend.ps1
```

Then open:

```text
http://127.0.0.1:3010
```

## 11. Direct frontend-only workflow

```powershell
cd frontend
Copy-Item .env.example .env.local
npm ci
npm run typecheck
npm run build
npm run dev
```

Frontend runs on `http://127.0.0.1:3010`.

## 12. Before committing or deploying

```powershell
.\scripts\verify.ps1
```

With both services running, also run:

```powershell
.\scripts\smoke-test.ps1
```

## Docker alternative

Use Docker instead of the direct Windows processes:

```powershell
docker compose up --build
```

Docker uses the same ONA Towers ports:

- Frontend: `3010`
- Backend: `8400`

Do not run the Docker services and direct local services on the same ports at the same time.

## Supabase/PostgreSQL option

SQLite is recommended for day-to-day local work. If you intentionally want to run the backend against Supabase/PostgreSQL, replace the database values in `.env` with the exact connection strings supplied by Supabase:

```env
DATABASE_URL=postgresql+psycopg://...
MIGRATION_DATABASE_URL=postgresql+psycopg://...
```

Then run:

```powershell
python scripts\doctor.py
```

You must see:

```text
[ OK ] PostgreSQL/Supabase connection and authentication work.
```

If authentication fails, correct the connection string/password in `.env`; do not edit Alembic migration files to work around a credential problem.

## Secrets

Never commit `.env`, Supabase connection strings/passwords, production admin passwords, session secrets, or SMTP credentials.
