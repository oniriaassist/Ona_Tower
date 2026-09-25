# ONA Towers — Start Here in VS Code

Open the `ONA_Tower` repository root in VS Code and use PowerShell terminals.

## First-time setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
.\scripts\configure-local.ps1
cd frontend
npm ci
cd ..
python scripts\doctor.py
python -m alembic -c database\alembic.ini upgrade head
python seed.py
python scripts\db_check.py
python -m pytest -c backend\pyproject.toml backend\tests -q
```

## Start the project

Terminal 1:

```powershell
.\.venv\Scripts\Activate.ps1
.\scripts\start-backend.ps1
```

Terminal 2:

```powershell
.\scripts\start-frontend.ps1
```

Open:

- Website: `http://127.0.0.1:3010`
- Admin: `http://127.0.0.1:3010/admin`
- Backend: `http://127.0.0.1:8400`
- Swagger/API docs: `http://127.0.0.1:8400/docs`
- Health: `http://127.0.0.1:8400/health`

## Check the running stack

```powershell
.\scripts\smoke-test.ps1
```

## Check before Git push/deployment

```powershell
.\scripts\verify.ps1
```

For more detail, read [`LOCAL_DEVELOPMENT.md`](LOCAL_DEVELOPMENT.md).
