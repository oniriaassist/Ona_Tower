# ONA Towers — Full-Stack Monorepo

ONA Towers is organized as one repository with separate frontend, backend, database, and operational layers.

For production deployment through one Vercel Services project with Supabase, follow [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md). Deploy from the repository root.

```text
ONA_Tower/
├── backend/              # FastAPI application
│   ├── app/
│   ├── tests/
│   ├── main.py           # Vercel Services FastAPI entrypoint
│   ├── requirements.txt
│   └── pyproject.toml
├── database/             # Alembic schema management + local SQLite database
│   ├── migrations/
│   ├── alembic.ini
│   └── README.md
├── frontend/             # Vite + React public site and admin workspace
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── scripts/              # Configure / doctor / run / migrate / verify commands
├── docs/                 # Development and deployment documentation
├── .env.example
├── requirements.txt      # Root Python requirements wrapper
├── seed.py               # Root seed command
├── Dockerfile
├── docker-compose.yml
├── package.json
└── vercel.json
```

## Local setup on Windows

The primary local workflow is intentionally explicit so every layer can be checked independently.

Use **Python 3.13** and **Node.js 22**. Run these commands from the repository root (`ONA_Tower/`).

### 1. Create and activate the virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation for the current terminal:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

Python 3.13 is required by `backend/pyproject.toml`.

### 2. Create `.env` safely

```powershell
.\scripts\configure-local.ps1
```

The normal local configuration uses SQLite at:

```text
database/ona_towers.db
```

Therefore PostgreSQL/Supabase is **not required** for normal local development.

The ONA Towers local ports remain:

- Frontend: `3010`
- FastAPI backend: `8400`

### 3. Install frontend dependencies

```powershell
cd frontend
npm ci
cd ..
```

### 4. Confirm the environment before running Alembic

```powershell
python scripts\doctor.py
```

A correct local setup ends with:

```text
[ OK ] SQLite connection and authentication work.
ALL LOCAL PREREQUISITE CHECKS PASSED
```

If you deliberately configure Supabase/PostgreSQL, the database line will report PostgreSQL/Supabase instead.

### 5. Create/update tables and seed ONA content

```powershell
python -m alembic -c database\alembic.ini upgrade head
python seed.py
python scripts\db_check.py
python -m pytest -c backend\pyproject.toml backend\tests -q
```

Expected Alembic head:

```text
c4f2a31b7d90 (head)
```

You can use this convenience equivalent after the environment has been created:

```powershell
.\scripts\migrate-database.ps1
```

### 6. Start backend

Terminal 1:

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\start-backend.ps1
```

Direct equivalent:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8400
```

Verify:

- `http://127.0.0.1:8400/health`
- `http://127.0.0.1:8400/docs`
- `http://127.0.0.1:8400/api/residences`

### 7. Start frontend in a second PowerShell terminal

```powershell
.\scripts\start-frontend.ps1
```

Open:

- Website: `http://127.0.0.1:3010`
- Admin: `http://127.0.0.1:3010/admin`

The Vite development server proxies `/api` and `/health` to FastAPI on port `8400`.

### 8. Test the complete running stack

Keep both servers running. In Terminal 3:

```powershell
.\scripts\smoke-test.ps1
```

A successful check ends with:

```text
ALL LOCAL CHECKS PASSED
```

### 9. Run all checks before pushing or deploying

```powershell
.\scripts\verify.ps1
```

This runs backend tests, reports the Alembic revision, type-checks the React frontend, and creates a production frontend build.

## Direct frontend setup (alternative)

If you only need to work on the React/Vite website:

```powershell
cd frontend
Copy-Item .env.example .env.local
npm ci
npm run typecheck
npm run build
npm run dev
```

Frontend: `http://127.0.0.1:3010`

The default Vite proxy target is `http://127.0.0.1:8400`.

## One-command dependency setup (optional)

The numbered manual steps above are the recommended first-time flow. If you later want the helper:

```powershell
.\scripts\setup-windows.ps1
```

It creates `.venv`, installs Python and frontend dependencies, and creates `.env` if needed. It intentionally **does not run migrations automatically**.

## Run the Vercel-style full stack together

If Vercel CLI is installed:

```powershell
.\scripts\start-vercel.ps1
```

or:

```powershell
npm run dev
```

This uses `vercel dev -L`, so both services run through the same Vercel routing model.

## Docker alternative

Use Docker instead of the direct Windows processes:

```powershell
docker compose up --build
```

Docker exposes:

- Frontend: `http://127.0.0.1:3010`
- Backend: `http://127.0.0.1:8400`

Do not run the direct local servers on ports `3010`/`8400` at the same time as Docker.

## Database migration safety

Alembic owns schema changes. Migration `c4f2a31b7d90` checks whether `admin_team_members.department` already exists before trying to add it, preventing the previous SQLite failure:

```text
sqlite3.OperationalError: duplicate column name: department
```

## Local vs production database

### Local

The default local `.env` uses:

```env
DATABASE_URL=sqlite+pysqlite:///./database/ona_towers.db
```

### Production

Use Supabase PostgreSQL:

- `DATABASE_URL` — runtime connection for FastAPI.
- `MIGRATION_DATABASE_URL` — migration connection for Alembic.

Never expose either value to the frontend.

## Secrets

Never commit:

- `.env`
- Supabase database URLs/passwords
- production administrator passwords
- session secrets
- SMTP credentials

Only safe templates such as `.env.example` should be committed.

## Local URLs

| Service | URL |
|---|---|
| Frontend | `http://127.0.0.1:3010` |
| Admin | `http://127.0.0.1:3010/admin` |
| Backend | `http://127.0.0.1:8400` |
| API docs | `http://127.0.0.1:8400/docs` |
| Health | `http://127.0.0.1:8400/health` |
| Residences API | `http://127.0.0.1:8400/api/residences` |

## Production architecture

```text
Browser
   │
   ▼
One Vercel Project
   ├── /api/*  ─────► FastAPI service (backend/)
   └── /*      ─────► Vite service (frontend/)
                         │
FastAPI ─────────────────┘
   │
   ▼
Supabase PostgreSQL
```

The frontend uses the same-origin `/api` path in production, so there is no second frontend/backend Vercel URL to maintain.

See [`docs/LOCAL_DEVELOPMENT.md`](docs/LOCAL_DEVELOPMENT.md) for the full numbered Windows workflow and [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for production deployment.
