from __future__ import annotations

from pathlib import Path
import os
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


def ok(message: str) -> None:
    print(f"[ OK ] {message}")


def fail(message: str) -> None:
    print(f"[FAIL] {message}")


def find_command(name: str) -> str | None:
    """
    Find an executable in PATH.

    On Windows, npm/npx are normally .cmd files,
    so explicitly check for those.
    """
    candidates = [name]

    if os.name == "nt":
        candidates = [
            f"{name}.exe",
            f"{name}.cmd",
            f"{name}.bat",
            name,
        ]

    for candidate in candidates:
        path = shutil.which(candidate)
        if path:
            return path

    return None


def command_version(name: str, label: str) -> bool:
    executable = find_command(name)

    if not executable:
        fail(f"{label} is not available in PATH.")
        return False

    try:
        result = subprocess.run(
            [executable, "--version"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )

        output = (result.stdout or result.stderr).strip()

        if not output:
            fail(f"{label} returned no version information.")
            return False

        first = output.splitlines()[0]
        ok(f"{label}: {first}")
        return True

    except subprocess.CalledProcessError as exc:
        error_message = (
            (exc.stderr or exc.stdout or "").strip()
            or f"exit code {exc.returncode}"
        )
        fail(f"{label} check failed: {error_message}")
        return False

    except OSError as exc:
        fail(f"{label} is not available: {exc}")
        return False


def main() -> int:
    failures = 0

    # ---------------------------------------------------------
    # Python
    # ---------------------------------------------------------

    version = sys.version_info

    if version.major == 3 and version.minor == 13:
        ok(
            f"Python "
            f"{version.major}.{version.minor}.{version.micro} "
            f"is supported."
        )
    else:
        fail(
            "Python 3.13 is required by backend/pyproject.toml; "
            f"found {version.major}.{version.minor}.{version.micro}."
        )
        failures += 1

    # ---------------------------------------------------------
    # Virtual environment
    # ---------------------------------------------------------

    if (ROOT / ".venv").exists():
        ok("Root virtual environment .venv exists.")
    else:
        fail("Root virtual environment .venv is missing.")
        failures += 1

    # ---------------------------------------------------------
    # Environment file
    # ---------------------------------------------------------

    if (ROOT / ".env").exists():
        ok("Root .env exists.")
    else:
        fail(
            "Root .env is missing. "
            "Run .\\scripts\\configure-local.ps1"
        )
        failures += 1

    # ---------------------------------------------------------
    # Node.js / npm
    # ---------------------------------------------------------

    if not command_version("node", "Node.js"):
        failures += 1

    if not command_version("npm", "npm"):
        failures += 1

    # ---------------------------------------------------------
    # Frontend dependencies
    # ---------------------------------------------------------

    if (ROOT / "frontend" / "node_modules").exists():
        ok("Frontend node_modules exists.")
    else:
        fail(
            "Frontend dependencies are missing. "
            "Run: cd frontend; npm ci"
        )
        failures += 1

    # ---------------------------------------------------------
    # Database
    # ---------------------------------------------------------

    try:
        from sqlalchemy import create_engine, text
        from app.core.config import get_settings

        get_settings.cache_clear()
        settings = get_settings()

        engine = create_engine(
            settings.sqlalchemy_database_url
        )

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        database_kind = (
            "SQLite"
            if settings.sqlalchemy_database_url.startswith("sqlite")
            else "PostgreSQL/Supabase"
        )

        ok(
            f"{database_kind} connection "
            "and authentication work."
        )

    except Exception as exc:
        fail(
            f"Database connection failed: "
            f"{type(exc).__name__}: {exc}"
        )
        failures += 1

    # ---------------------------------------------------------
    # Final result
    # ---------------------------------------------------------

    print()

    if failures:
        print(
            f"Doctor found {failures} problem(s). "
            "Fix them before migrations/startup."
        )
        return 1

    print("ALL LOCAL PREREQUISITE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())