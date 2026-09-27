from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import AppError
from app.database.models import AdminTeamMember
from app.database.session import get_db_session

_DEV_SECRET = "ona-local-development-secret"


@dataclass(frozen=True)
class AdminPrincipal:
    id: str
    email: str
    name: str
    role: str
    department: str | None
    is_super_admin: bool


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def validate_production_admin_config(settings: Settings) -> None:
    """Validate only the secret required to sign admin sessions.

    Admin passwords are stored as hashes in ``admin_team_members``. Their
    strength is enforced when accounts are created/changed, so the bootstrap
    environment password must not disable a valid database-backed admin account.
    """
    if settings.app_env != "production":
        return
    if len(settings.admin_session_secret) < 32 or settings.admin_session_secret == _DEV_SECRET:
        raise AppError(
            "Admin session security is not configured for production.",
            code="admin_session_not_configured",
            status_code=503,
        )


def create_admin_token(settings: Settings, member: AdminTeamMember) -> tuple[str, int]:
    validate_production_admin_config(settings)
    expires_at = int(time.time()) + settings.admin_session_hours * 3600
    payload = json.dumps(
        {"id": member.id, "email": member.email, "exp": expires_at},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    payload_part = _b64encode(payload)
    signature = hmac.new(
        settings.admin_session_secret.encode("utf-8"),
        payload_part.encode("ascii"),
        hashlib.sha256,
    ).digest()
    return f"{payload_part}.{_b64encode(signature)}", expires_at


def _read_token(settings: Settings, token: str) -> tuple[str, str]:
    validate_production_admin_config(settings)
    try:
        payload_part, signature_part = token.split(".", 1)
        expected = hmac.new(
            settings.admin_session_secret.encode("utf-8"),
            payload_part.encode("ascii"),
            hashlib.sha256,
        ).digest()
        supplied = _b64decode(signature_part)
        if not hmac.compare_digest(expected, supplied):
            raise ValueError("signature mismatch")
        payload = json.loads(_b64decode(payload_part))
        member_id = str(payload["id"])
        email = str(payload["email"]).lower()
        expires_at = int(payload["exp"])
    except Exception as exc:
        raise AppError(
            "Your admin session is invalid. Please sign in again.",
            code="admin_unauthorized",
            status_code=401,
        ) from exc

    if expires_at <= int(time.time()):
        raise AppError(
            "Your admin session has expired. Please sign in again.",
            code="admin_session_expired",
            status_code=401,
        )
    return member_id, email


def require_admin(
    request: Request,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db_session),
) -> AdminPrincipal:
    authorization = request.headers.get("authorization", "")
    if not authorization.lower().startswith("bearer "):
        raise AppError("Admin authentication is required.", code="admin_unauthorized", status_code=401)
    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise AppError("Admin authentication is required.", code="admin_unauthorized", status_code=401)

    member_id, email = _read_token(settings, token)
    member = db.get(AdminTeamMember, member_id)
    if member is None or not member.active or member.email.lower() != email:
        raise AppError(
            "Your admin account is no longer available. Please sign in again.",
            code="admin_unauthorized",
            status_code=401,
        )
    return AdminPrincipal(
        id=member.id,
        email=member.email,
        name=member.name,
        role=member.role,
        department=member.department,
        is_super_admin=member.is_super_admin,
    )


def require_super_admin(principal: AdminPrincipal = Depends(require_admin)) -> AdminPrincipal:
    if not principal.is_super_admin:
        raise AppError(
            "Administrator permission is required for this action.",
            code="admin_forbidden",
            status_code=403,
        )
    return principal
