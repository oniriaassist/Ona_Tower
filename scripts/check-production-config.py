"""Validate a production env file without connecting to or modifying a database."""

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from pydantic import ValidationError
from app.core.config import Settings, production_configuration_errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("env_file", type=Path, help="Production environment file to validate")
    args = parser.parse_args()
    if not args.env_file.is_file():
        print("Environment file not found.")
        return 1
    try:
        settings = Settings(_env_file=str(args.env_file))
    except ValidationError as exc:
        for error in exc.errors(include_input=False, include_context=False):
            print("Invalid setting: " + ".".join(str(part) for part in error["loc"]))
        return 1
    errors = production_configuration_errors(settings)
    if settings.app_env != "production" and "APP_ENV must be set to production" not in errors:
        errors.insert(0, "APP_ENV must be set to production")
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Production configuration: PASS (database connectivity not checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
