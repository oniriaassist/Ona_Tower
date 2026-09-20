# ONA Towers — Full-Stack Monorepo

ONA Towers is organized as one repository with separate frontend, backend, database, and operational layers.

For one Vercel Services project with Supabase, follow
[the deployment guide](docs/DEPLOYMENT.md). Deploy from the repository root.

```text
ONA_Tower/
├── backend/              # FastAPI application
│   ├── app/
│   ├── tests/
│   ├── main.py           # Vercel Services FastAPI entrypoint
│   ├── requirements.txt
│   └── pyproject.toml
├── database/             # Alembic schema management
│   ├── migrations/
│   ├── alembic.ini
│   └── README.md
├── frontend/             # Vite + React public site and admin workspace
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── scripts/              # Focused setup/run/migrate/verify commands
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── package.json          # Root orchestration commands
├── vercel.json           # One Vercel project, two services
└── DEPLOYMENT.md
```

## Local setup on Windows

From the repository root:

```powershell
.\scripts\setup-windows.ps1
```

This installs Python and frontend dependencies. It **does not** run migrations automatically.

Then migrate and seed the database:

```powershell
.\scripts\migrate-database.ps1
```

### Run backend and frontend separately

Terminal 1:

```powershell
.\scripts\start-backend.ps1
```

Terminal 2:

```powershell
.\scripts\start-frontend.ps1
```

URLs:

- Frontend: `http://127.0.0.1:3010`
- Admin: `http://127.0.0.1:3010/admin`
- Backend: `http://127.0.0.1:8400`
- API docs: `http://127.0.0.1:8400/docs`
- Health: `http://127.0.0.1:8400/health`

The Vite development server proxies `/api` to FastAPI.

### Run the Vercel-style full stack together

If Vercel CLI is installed:

```powershell
.\scripts\start-vercel.ps1
```

or:

```powershell
npm run dev
```

This uses `vercel dev -L` so both services run through the same Vercel routing model.

## Database migration safety

Alembic owns schema changes. The admin migrations inspect existing columns before adding them. If an old SQLite database already contains `admin_team_members.department`, migration `c4f2a31b7d90` skips that column rather than issuing the failing command again.

This removes the previous failure:

```text
sqlite3.OperationalError: duplicate column name: department
```

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

See `docs/DEPLOYMENT.md` for production deployment and Supabase settings.
