from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta, timezone
import hmac

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.admin_auth import (
    AdminPrincipal,
    create_admin_token,
    require_admin,
    require_super_admin,
)
from app.core.config import Settings, get_settings
from app.core.exceptions import AppError, NotFoundError
from app.core.passwords import hash_password, verify_password
from app.database.models import AdminSetting, AdminTeamMember, Enquiry, SiteVisit
from app.database.session import get_db_session
from app.schemas.admin import (
    AdminAnalytics,
    AdminEnquiry,
    AdminEnquiryList,
    AdminEnquiryUpdate,
    AdminForgotPasswordRequest,
    AdminLoginRequest,
    AdminLoginResponse,
    AdminMeResponse,
    AdminOverview,
    AdminPasswordChange,
    AdminProfileUpdate,
    AdminSettingsPayload,
    AdminSettingsRecord,
    AdminUser,
    AnalyticsPoint,
    ApiMessage,
    TeamMemberCreate,
    TeamMemberResponse,
    TeamMemberUpdate,
    TeamPasswordReset,
    TopPage,
)

router = APIRouter(prefix="/admin", tags=["Admin"])
SETTINGS_KEY = "workspace"


def _settings_from_db(db: Session) -> tuple[AdminSettingsPayload, datetime | None]:
    record = db.get(AdminSetting, SETTINGS_KEY)
    if record is None or not isinstance(record.value, dict):
        return AdminSettingsPayload(), None
    try:
        return AdminSettingsPayload.model_validate(record.value), record.updated_at
    except Exception:
        return AdminSettingsPayload(), record.updated_at


def _enquiry_payload(row: Enquiry) -> AdminEnquiry:
    return AdminEnquiry(
        id=row.id,
        reference_number=row.reference_number,
        name=row.name,
        phone=row.phone,
        email=row.email,
        residence_interest=row.residence_interest,
        enquiry_type=row.enquiry_type,
        message=row.message,
        consent=row.consent,
        source=row.source,
        status=row.status,
        assigned_to=row.assigned_to,
        internal_notes=row.internal_notes,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _admin_user(row: AdminTeamMember) -> AdminUser:
    return AdminUser(
        id=row.id,
        name=row.name,
        email=row.email,
        phone=row.phone,
        role=row.role,
        department=row.department,
        is_super_admin=row.is_super_admin,
        active=row.active,
        last_login_at=row.last_login_at,
        password_reset_requested_at=row.password_reset_requested_at,
    )


def _team_payload(row: AdminTeamMember) -> TeamMemberResponse:
    return TeamMemberResponse(
        id=row.id,
        name=row.name,
        email=row.email,
        phone=row.phone,
        role=row.role,
        department=row.department,
        is_super_admin=row.is_super_admin,
        active=row.active,
        last_login_at=row.last_login_at,
        password_reset_requested_at=row.password_reset_requested_at,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


def _month_key(value: datetime) -> str:
    return f"{value.year:04d}-{value.month:02d}"


def _previous_months(count: int) -> list[tuple[int, int]]:
    now = datetime.now(timezone.utc)
    year, month = now.year, now.month
    values: list[tuple[int, int]] = []
    for _ in range(count):
        values.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    values.reverse()
    return values


def _analytics_payload(db: Session) -> AdminAnalytics:
    now = datetime.now(timezone.utc)
    day_start = (now - timedelta(days=13)).replace(hour=0, minute=0, second=0, microsecond=0)
    thirty_days_ago = now - timedelta(days=30)
    months = _previous_months(12)
    first_year, first_month = months[0]
    first_month_start = datetime(first_year, first_month, 1, tzinfo=timezone.utc)

    rows = db.scalars(
        select(SiteVisit).where(SiteVisit.visited_at >= first_month_start).order_by(SiteVisit.visited_at.asc())
    ).all()

    daily_counts: Counter[date] = Counter()
    monthly_counts: Counter[str] = Counter()
    top_page_counts: Counter[str] = Counter()
    sessions_30: set[str] = set()
    visits_30 = 0

    for row in rows:
        visited = row.visited_at
        if visited.tzinfo is None:
            visited = visited.replace(tzinfo=timezone.utc)
        if visited >= day_start:
            daily_counts[visited.date()] += 1
        monthly_counts[_month_key(visited)] += 1
        if visited >= thirty_days_ago:
            visits_30 += 1
            sessions_30.add(row.session_id)
            top_page_counts[row.page_path] += 1

    daily = []
    for offset in range(14):
        current = (day_start + timedelta(days=offset)).date()
        daily.append(AnalyticsPoint(label=current.strftime("%d %b"), value=daily_counts[current]))

    monthly = []
    for year, month in months:
        key = f"{year:04d}-{month:02d}"
        label = datetime(year, month, 1).strftime("%b %y")
        monthly.append(AnalyticsPoint(label=label, value=monthly_counts[key]))

    top_pages = [
        TopPage(path=path, visits=count)
        for path, count in top_page_counts.most_common(6)
    ]
    return AdminAnalytics(
        total_visits_30_days=visits_30,
        unique_sessions_30_days=len(sessions_30),
        daily=daily,
        monthly=monthly,
        top_pages=top_pages,
    )


def _ensure_not_last_super_admin(db: Session, row: AdminTeamMember, next_super: bool, next_active: bool) -> None:
    if not row.is_super_admin or (next_super and next_active):
        return
    remaining = db.scalar(
        select(func.count()).select_from(AdminTeamMember).where(
            AdminTeamMember.id != row.id,
            AdminTeamMember.is_super_admin.is_(True),
            AdminTeamMember.active.is_(True),
        )
    ) or 0
    if remaining == 0:
        raise AppError(
            "At least one active administrator account is required.",
            code="last_admin_required",
            status_code=422,
        )


@router.post("/login", response_model=AdminLoginResponse)
async def login(
    payload: AdminLoginRequest,
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db_session),
):
    email = str(payload.email).strip().lower()
    member = db.scalar(select(AdminTeamMember).where(func.lower(AdminTeamMember.email) == email))

    bootstrap_email = settings.admin_email.strip().lower()
    bootstrap_password = settings.admin_password
    production_default_password = bootstrap_password == "ona-admin-local"
    bootstrap_credentials_match = (
        email == bootstrap_email
        and len(bootstrap_password) >= 8
        and not (settings.app_env == "production" and production_default_password)
        and hmac.compare_digest(payload.password, bootstrap_password)
    )

    # Recovery/bootstrap path for the primary administrator. This keeps the
    # server-side ADMIN_EMAIL/ADMIN_PASSWORD pair useful if the database was
    # migrated without seeding, or if the bootstrap password was deliberately
    # rotated in Vercel after the original admin row was created.
    if member is None and bootstrap_credentials_match:
        member = AdminTeamMember(
            name=settings.admin_name.strip() or "ONA Administrator",
            email=bootstrap_email,
            role=settings.admin_role.strip() or "Administrator",
            department=settings.admin_department.strip() or None,
            password_hash=hash_password(bootstrap_password),
            is_super_admin=True,
            active=True,
        )
        db.add(member)
        db.flush()

    password_ok = member is not None and verify_password(payload.password, member.password_hash)
    if member is not None and not password_ok and bootstrap_credentials_match:
        member.password_hash = hash_password(bootstrap_password)
        member.is_super_admin = True
        member.active = True
        password_ok = True

    if member is None or not member.active or not password_ok:
        raise AppError(
            "Invalid staff email or password.",
            code="admin_invalid_credentials",
            status_code=401,
        )

    member.last_login_at = datetime.now(timezone.utc)
    member.password_reset_requested_at = None
    db.add(member)
    db.commit()
    db.refresh(member)
    token, expires_at = create_admin_token(settings, member)
    return AdminLoginResponse(token=token, expires_at=expires_at, user=_admin_user(member))


@router.post("/forgot-password", response_model=ApiMessage)
async def forgot_password(
    payload: AdminForgotPasswordRequest,
    db: Session = Depends(get_db_session),
):
    email = str(payload.email).strip().lower()
    member = db.scalar(select(AdminTeamMember).where(func.lower(AdminTeamMember.email) == email))
    if member is not None and member.active:
        member.password_reset_requested_at = datetime.now(timezone.utc)
        member.updated_at = datetime.now(timezone.utc)
        db.add(member)
        db.commit()
    # Same response for known/unknown emails to avoid account discovery.
    return ApiMessage(message="If that staff account exists, a password reset request has been recorded.")


@router.get("/me", response_model=AdminMeResponse)
async def admin_me(
    principal: AdminPrincipal = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    member = db.get(AdminTeamMember, principal.id)
    if member is None:
        raise NotFoundError("Staff account not found.")
    return AdminMeResponse(user=_admin_user(member))


@router.patch("/profile", response_model=AdminLoginResponse)
async def update_profile(
    payload: AdminProfileUpdate,
    principal: AdminPrincipal = Depends(require_admin),
    settings: Settings = Depends(get_settings),
    db: Session = Depends(get_db_session),
):
    member = db.get(AdminTeamMember, principal.id)
    if member is None:
        raise NotFoundError("Staff account not found.")
    member.name = payload.name.strip()
    member.email = str(payload.email).lower()
    member.phone = payload.phone.strip() if payload.phone else None
    member.updated_at = datetime.now(timezone.utc)
    db.add(member)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppError("A staff account with this email already exists.", code="team_email_exists", status_code=409) from exc
    db.refresh(member)
    token, expires_at = create_admin_token(settings, member)
    return AdminLoginResponse(token=token, expires_at=expires_at, user=_admin_user(member))


@router.post("/security/password", response_model=ApiMessage)
async def change_password(
    payload: AdminPasswordChange,
    principal: AdminPrincipal = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    member = db.get(AdminTeamMember, principal.id)
    if member is None:
        raise NotFoundError("Staff account not found.")
    if not verify_password(payload.current_password, member.password_hash):
        raise AppError("Current password is incorrect.", code="invalid_current_password", status_code=422)
    member.password_hash = hash_password(payload.new_password)
    member.password_reset_requested_at = None
    member.updated_at = datetime.now(timezone.utc)
    db.add(member)
    db.commit()
    return ApiMessage(message="Password updated successfully.")


@router.get("/overview", response_model=AdminOverview)
async def overview(
    _: AdminPrincipal = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    total = db.scalar(select(func.count()).select_from(Enquiry)) or 0
    new_count = db.scalar(select(func.count()).select_from(Enquiry).where(Enquiry.status == "new")) or 0
    closed = db.scalar(
        select(func.count()).select_from(Enquiry).where(Enquiry.status.in_(["closed", "archived"]))
    ) or 0
    active = max(total - closed, 0)
    seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
    recent_count = db.scalar(
        select(func.count()).select_from(Enquiry).where(Enquiry.created_at >= seven_days_ago)
    ) or 0
    active_team = db.scalar(
        select(func.count()).select_from(AdminTeamMember).where(AdminTeamMember.active.is_(True))
    ) or 0
    recent_rows = db.scalars(select(Enquiry).order_by(Enquiry.created_at.desc()).limit(6)).all()
    workspace_settings, _ = _settings_from_db(db)
    overdue_before = datetime.now(timezone.utc) - timedelta(hours=workspace_settings.response_sla_hours)
    overdue = db.scalar(
        select(func.count()).select_from(Enquiry).where(
            Enquiry.created_at < overdue_before,
            ~Enquiry.status.in_(["closed", "archived"]),
        )
    ) or 0

    return AdminOverview(
        total_enquiries=total,
        new_enquiries=new_count,
        active_enquiries=active,
        closed_enquiries=closed,
        enquiries_last_7_days=recent_count,
        active_team_members=active_team,
        overdue_enquiries=overdue,
        recent_enquiries=[_enquiry_payload(row) for row in recent_rows],
        settings=workspace_settings,
        analytics=_analytics_payload(db),
    )


@router.get("/enquiries", response_model=AdminEnquiryList)
async def list_enquiries(
    search: str = Query(default="", max_length=200),
    status: str = Query(default="all", max_length=40),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    _: AdminPrincipal = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    filters = []
    term = search.strip()
    if term:
        wildcard = f"%{term}%"
        filters.append(or_(
            Enquiry.name.ilike(wildcard), Enquiry.email.ilike(wildcard),
            Enquiry.phone.ilike(wildcard), Enquiry.reference_number.ilike(wildcard),
            Enquiry.residence_interest.ilike(wildcard),
        ))
    if status and status != "all":
        filters.append(Enquiry.status == status)
    count_stmt = select(func.count()).select_from(Enquiry)
    rows_stmt = select(Enquiry)
    if filters:
        count_stmt = count_stmt.where(*filters)
        rows_stmt = rows_stmt.where(*filters)
    total = db.scalar(count_stmt) or 0
    rows = db.scalars(rows_stmt.order_by(Enquiry.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return AdminEnquiryList(items=[_enquiry_payload(row) for row in rows], total=total, page=page, page_size=page_size)


@router.get("/enquiries/{enquiry_id}", response_model=AdminEnquiry)
async def get_enquiry(
    enquiry_id: str,
    _: AdminPrincipal = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    row = db.get(Enquiry, enquiry_id)
    if row is None:
        raise NotFoundError("Enquiry not found.")
    return _enquiry_payload(row)


@router.patch("/enquiries/{enquiry_id}", response_model=AdminEnquiry)
async def update_enquiry(
    enquiry_id: str,
    payload: AdminEnquiryUpdate,
    _: AdminPrincipal = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    row = db.get(Enquiry, enquiry_id)
    if row is None:
        raise NotFoundError("Enquiry not found.")
    fields = payload.model_fields_set
    if "status" in fields and payload.status is not None:
        row.status = payload.status
    if "assigned_to" in fields:
        if payload.assigned_to:
            member = db.get(AdminTeamMember, payload.assigned_to)
            if member is None or not member.active:
                raise AppError("The selected staff member is not available.", code="invalid_assignee", status_code=422)
        row.assigned_to = payload.assigned_to or None
    if "internal_notes" in fields:
        row.internal_notes = payload.internal_notes.strip() if payload.internal_notes else None
    row.updated_at = datetime.now(timezone.utc)
    db.add(row)
    db.commit()
    db.refresh(row)
    return _enquiry_payload(row)


@router.get("/team", response_model=list[TeamMemberResponse])
async def list_team(
    include_inactive: bool = False,
    _: AdminPrincipal = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    stmt = select(AdminTeamMember)
    if not include_inactive:
        stmt = stmt.where(AdminTeamMember.active.is_(True))
    rows = db.scalars(stmt.order_by(AdminTeamMember.name.asc())).all()
    return [_team_payload(row) for row in rows]


@router.post("/team", response_model=TeamMemberResponse, status_code=201)
async def create_team_member(
    payload: TeamMemberCreate,
    _: AdminPrincipal = Depends(require_super_admin),
    db: Session = Depends(get_db_session),
):
    row = AdminTeamMember(
        name=payload.name.strip(),
        email=str(payload.email).lower(),
        phone=payload.phone.strip() if payload.phone else None,
        role=payload.role.strip(),
        department=payload.department.strip() if payload.department else None,
        password_hash=hash_password(payload.password),
        is_super_admin=payload.is_super_admin,
        active=payload.active,
    )
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppError("A staff account with this email already exists.", code="team_email_exists", status_code=409) from exc
    db.refresh(row)
    return _team_payload(row)


@router.patch("/team/{member_id}", response_model=TeamMemberResponse)
async def update_team_member(
    member_id: str,
    payload: TeamMemberUpdate,
    principal: AdminPrincipal = Depends(require_super_admin),
    db: Session = Depends(get_db_session),
):
    row = db.get(AdminTeamMember, member_id)
    if row is None:
        raise NotFoundError("Staff member not found.")
    fields = payload.model_fields_set
    next_super = payload.is_super_admin if "is_super_admin" in fields and payload.is_super_admin is not None else row.is_super_admin
    next_active = payload.active if "active" in fields and payload.active is not None else row.active
    if principal.id == row.id and not next_active:
        raise AppError("You cannot remove your own access while signed in.", code="cannot_deactivate_self", status_code=422)
    _ensure_not_last_super_admin(db, row, next_super, next_active)

    if "name" in fields and payload.name is not None: row.name = payload.name.strip()
    if "email" in fields and payload.email is not None: row.email = str(payload.email).lower()
    if "phone" in fields: row.phone = payload.phone.strip() if payload.phone else None
    if "role" in fields and payload.role is not None: row.role = payload.role.strip()
    if "department" in fields: row.department = payload.department.strip() if payload.department else None
    if "is_super_admin" in fields and payload.is_super_admin is not None: row.is_super_admin = payload.is_super_admin
    if "active" in fields and payload.active is not None: row.active = payload.active
    row.updated_at = datetime.now(timezone.utc)
    db.add(row)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppError("A staff account with this email already exists.", code="team_email_exists", status_code=409) from exc
    db.refresh(row)
    return _team_payload(row)


@router.post("/team/{member_id}/reset-password", response_model=ApiMessage)
async def reset_team_password(
    member_id: str,
    payload: TeamPasswordReset,
    _: AdminPrincipal = Depends(require_super_admin),
    db: Session = Depends(get_db_session),
):
    row = db.get(AdminTeamMember, member_id)
    if row is None:
        raise NotFoundError("Staff member not found.")
    row.password_hash = hash_password(payload.new_password)
    row.password_reset_requested_at = None
    row.updated_at = datetime.now(timezone.utc)
    db.add(row)
    db.commit()
    return ApiMessage(message="Temporary password saved. Ask the staff member to sign in and change it.")


@router.delete("/team/{member_id}", response_model=ApiMessage)
async def delete_team_member(
    member_id: str,
    principal: AdminPrincipal = Depends(require_super_admin),
    db: Session = Depends(get_db_session),
):
    row = db.get(AdminTeamMember, member_id)
    if row is None:
        raise NotFoundError("Staff member not found.")
    if principal.id == row.id:
        raise AppError("You cannot remove your own access while signed in.", code="cannot_deactivate_self", status_code=422)
    _ensure_not_last_super_admin(db, row, row.is_super_admin, False)
    row.active = False
    row.updated_at = datetime.now(timezone.utc)
    db.add(row)
    db.commit()
    return ApiMessage(message="Staff access removed. Historical enquiry assignments were preserved.")


@router.get("/settings", response_model=AdminSettingsRecord)
async def get_admin_settings(
    _: AdminPrincipal = Depends(require_admin),
    db: Session = Depends(get_db_session),
):
    workspace_settings, updated_at = _settings_from_db(db)
    return AdminSettingsRecord(settings=workspace_settings, updated_at=updated_at)


@router.patch("/settings", response_model=AdminSettingsRecord)
async def update_admin_settings(
    payload: AdminSettingsPayload,
    _: AdminPrincipal = Depends(require_super_admin),
    db: Session = Depends(get_db_session),
):
    row = db.get(AdminSetting, SETTINGS_KEY)
    now = datetime.now(timezone.utc)
    values = payload.model_dump(mode="json")
    if row is None:
        row = AdminSetting(key=SETTINGS_KEY, value=values, updated_at=now)
    else:
        row.value = values
        row.updated_at = now
    db.add(row)
    db.commit()
    db.refresh(row)
    return AdminSettingsRecord(settings=payload, updated_at=row.updated_at)
