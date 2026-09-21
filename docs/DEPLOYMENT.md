# ONA Towers Deployment — Vercel Services + Supabase

## Target architecture

Use the existing `new_ona_tower` project with Root Directory blank (repository
root) and Framework Preset **Services**. Keep its existing domain. The root
`vercel.json` is the only deployment configuration; nested configurations have
been removed. See [Vercel's Services guide](https://vercel.com/kb/guide/vercel-services).

ONA Towers deploys as **one Vercel project** using Vercel Services:

- `frontend/` — Vite + React service
- `backend/` — FastAPI service
- `database/` — Alembic migrations only; this folder is not an application service
- Supabase — PostgreSQL database

The root `vercel.json` owns public routing:

- `/api` and `/api/*` -> FastAPI
- `/health` and `/health/*` -> FastAPI
- all other routes -> Vite frontend

The frontend calls the API through the same origin with `VITE_API_BASE_URL=/api`. Deep frontend URLs such as `/admin`, `/residences`, and `/location` are rewritten to `index.html` inside the frontend service so browser refreshes continue to work.

## 1. Create the Supabase database

Create a Supabase project, then open **Connect** in the Supabase dashboard. Copy the connection strings from Supabase instead of manually constructing hosts.

### Runtime connection for Vercel

Use the **Transaction pooler** connection string, normally port `6543`, as `DATABASE_URL`. It is appropriate for serverless/auto-scaling workloads. The backend disables psycopg prepared statements and uses SQLAlchemy `NullPool` for production.

Example shape only:

```env
DATABASE_URL=postgresql+psycopg://postgres.PROJECT_REF:PASSWORD@POOLER_HOST:6543/postgres?sslmode=require
```

### Migration connection

Use a **Session pooler** connection string, normally port `5432`, or a direct connection when your machine supports the required network path. Store it locally/CI as `MIGRATION_DATABASE_URL`; do not expose it to frontend code.

Example shape only:

```env
MIGRATION_DATABASE_URL=postgresql+psycopg://postgres.PROJECT_REF:PASSWORD@POOLER_HOST:5432/postgres?sslmode=require
```

If your database password contains reserved URL characters, use the exact encoded connection string supplied by Supabase.

## 2. Prepare local migration environment

From the repository root, copy `.env.example` to `.env` and replace the database/admin values with production values. Do not commit `.env`.

Production requires:

```env
APP_ENV=production
APP_DEBUG=false
API_PREFIX=/api
AUTO_INIT_DB=false
DATABASE_URL=YOUR_SUPABASE_TRANSACTION_POOLER_URL
MIGRATION_DATABASE_URL=YOUR_SUPABASE_SESSION_OR_DIRECT_URL

ADMIN_EMAIL=YOUR_REAL_ADMIN_EMAIL
ADMIN_PASSWORD=YOUR_UNIQUE_PASSWORD_OF_AT_LEAST_12_CHARACTERS
ADMIN_NAME=ONA Administrator
ADMIN_ROLE=Administrator
ADMIN_DEPARTMENT=Administration
ADMIN_SESSION_SECRET=YOUR_RANDOM_SECRET_OF_AT_LEAST_32_CHARACTERS
ADMIN_SESSION_HOURS=12
```

Generate a strong session secret with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

The backend now fails fast in `APP_ENV=production` when the database/admin settings are missing or still use local-development defaults.

## 3. Run migrations and seed once before first production use

Windows helper:

```powershell
.\scripts\setup-windows.ps1
.\scripts\migrate-database.ps1
```

Equivalent commands from the repository root:

```powershell
$env:PYTHONPATH = "$PWD\backend"
.\.venv\Scripts\python.exe -m alembic -c database\alembic.ini upgrade head
.\.venv\Scripts\python.exe scripts\db_seed.py
.\.venv\Scripts\python.exe scripts\db_check.py
```

Expected final migration revision:

```text
c4f2a31b7d90 (head)
```

Do **not** run Alembic automatically on every Vercel request or function startup.

## 4. Run local verification before deployment

Backend tests:

```powershell
python -m pytest -c backend/pyproject.toml backend/tests -q
```

Frontend typecheck + production build:

```powershell
cd frontend
npm ci
npm run check
cd ..
```

Optional full-stack Vercel routing test after installing Vercel CLI:

```powershell
npm run dev
```

This runs `vercel dev -L` from the repository root.

## 5. Import the Git repository into Vercel

Create **one Vercel project from the repository root**. Do not create separate Vercel projects for `frontend/` and `backend/`.

The root `vercel.json` defines both services. Vercel builds them independently and deploys them together behind one domain.

## 6. Configure Vercel environment variables

Add these in **Project Settings -> Environment Variables**. Use the real values for Production; add Preview values too if preview deployments must use the backend/database.

```env
APP_ENV=production
APP_DEBUG=false
API_PREFIX=/api
AUTO_INIT_DB=false
DATABASE_URL=YOUR_SUPABASE_TRANSACTION_POOLER_URL

ADMIN_EMAIL=YOUR_ADMIN_EMAIL
ADMIN_PASSWORD=YOUR_STRONG_ADMIN_PASSWORD
ADMIN_NAME=ONA Administrator
ADMIN_ROLE=Administrator
ADMIN_DEPARTMENT=Administration
ADMIN_SESSION_SECRET=YOUR_LONG_RANDOM_SECRET
ADMIN_SESSION_HOURS=12

VITE_API_BASE_URL=/api
```

Do **not** add `MIGRATION_DATABASE_URL` to the frontend. It is normally unnecessary on Vercel because schema migrations should be run from a trusted migration job or local machine before release.

Same-origin production traffic does not need an extra CORS origin. Leave `CORS_ORIGINS` empty unless another external origin must directly call the API.

## 7. Deploy

Before deploying, validate your completed production environment file:

```powershell
.\.venv\Scripts\python.exe scripts\check-production-config.py .env.production
```

Process environment variables override file values. This check reports setting
names and requirements without printing secrets. It does not change Vercel
settings or test database connectivity. Copy the validated values into the
Vercel project's Production environment and redeploy.

If `/health/config` reports `ADMIN_PASSWORD`, set a unique password with at
least 12 characters in Vercel. Changing this environment variable does not
reset a password already stored in Supabase. Use the account's existing password
or the application's authenticated password-change workflow.

Push the connected Git branch, or deploy from the repository root with Vercel CLI:

```powershell
vercel
```

Production:

```powershell
vercel --prod
```

## 8. Verify after deployment

Replace `YOUR-DOMAIN` below with the Vercel/custom domain:

```text
https://YOUR-DOMAIN/
https://YOUR-DOMAIN/residences
https://YOUR-DOMAIN/admin
https://YOUR-DOMAIN/health
https://YOUR-DOMAIN/health/config
https://YOUR-DOMAIN/health/database
https://YOUR-DOMAIN/api/residences
```

Expected behavior:

- `/` and public pages render the Vite frontend.
- Refreshing a nested frontend route does not return a 404.
- `/health` returns the FastAPI liveness response.
- `/health/config` reports configuration errors without preventing startup.
  When production settings are invalid, other routes return 503 with
  `service_misconfigured`. This also applies when `VERCEL_ENV=production`
  but `APP_ENV` was not set correctly.
- `/health/database` reports `database: connected`.
- `/api/residences` returns seeded residence JSON.
- `/admin` loads the admin UI and the configured production admin can sign in.
- Creating an enquiry persists it in Supabase and it appears in the admin workspace.

Production Swagger/ReDoc are intentionally disabled when `APP_ENV=production`.

If importing the application fails, the `backend/main.py` entrypoint serves a
minimal `/health` response with HTTP 503, `stage: bootstrap`, and the exception
type. It does not expose exception messages or credentials; inspect server logs
for the traceback. This fallback requires FastAPI itself to be installed.
Configuration diagnostics likewise return a redacted exception type if checking
settings fails. Ordinary validation messages contain setting names, not values.

The public and admin API clients display supported server error messages and
fall back to the HTTP status when the response is not JSON. A successful health
check alone does not verify migrations, administrator credentials, or enquiries.

Keep `VITE_BACKEND_PROXY_TARGET` local; remove it from Vercel production.
Use `VITE_API_BASE_URL=/api`. Keep the migration URL on the migration machine.
Changing `ADMIN_PASSWORD` does not reset an existing seeded account's password.

## 9. Future schema changes

For every database schema change:

1. create/review a new Alembic migration under `database/migrations/versions/`;
2. apply it to Supabase with `MIGRATION_DATABASE_URL`;
3. run `scripts/db_check.py`;
4. deploy the matching application code.

Do not use `Base.metadata.create_all()` as a production migration strategy, and do not manually change the production schema without adding the matching Alembic migration.
