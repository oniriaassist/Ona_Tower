from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


EnquiryStatus = Literal[
    "new",
    "contacted",
    "qualified",
    "viewing_scheduled",
    "closed",
    "archived",
]


class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=500)


class AdminForgotPasswordRequest(BaseModel):
    email: EmailStr


class AdminUser(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: str | None = None
    role: str
    department: str | None = None
    is_super_admin: bool
    active: bool
    last_login_at: datetime | None = None
    password_reset_requested_at: datetime | None = None


class AdminLoginResponse(BaseModel):
    token: str
    token_type: str = "bearer"
    expires_at: int
    user: AdminUser


class AdminEnquiry(BaseModel):
    id: str
    reference_number: str
    name: str
    phone: str
    email: EmailStr | None = None
    residence_interest: str | None = None
    enquiry_type: str
    message: str | None = None
    consent: bool
    source: str
    status: str
    assigned_to: str | None = None
    internal_notes: str | None = None
    created_at: datetime
    updated_at: datetime | None = None


class AdminEnquiryList(BaseModel):
    items: list[AdminEnquiry]
    total: int
    page: int
    page_size: int


class AdminEnquiryUpdate(BaseModel):
    status: EnquiryStatus | None = None
    assigned_to: str | None = Field(default=None, max_length=36)
    internal_notes: str | None = Field(default=None, max_length=5000)


class TeamMemberCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)
    phone: str | None = Field(default=None, max_length=30)
    role: str = Field(default="Sales manager", min_length=2, max_length=80)
    department: str | None = Field(default=None, max_length=100)
    is_super_admin: bool = False
    active: bool = True

    @field_validator("name", "role", "phone", "department", mode="before")
    @classmethod
    def strip_text(cls, value):
        if isinstance(value, str):
            value = " ".join(value.strip().split())
            return value or None
        return value


class TeamMemberUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    role: str | None = Field(default=None, min_length=2, max_length=80)
    department: str | None = Field(default=None, max_length=100)
    is_super_admin: bool | None = None
    active: bool | None = None


class TeamPasswordReset(BaseModel):
    new_password: str = Field(min_length=8, max_length=200)


class TeamMemberResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    phone: str | None = None
    role: str
    department: str | None = None
    is_super_admin: bool
    active: bool
    last_login_at: datetime | None = None
    password_reset_requested_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class AdminProfileUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)

    @field_validator("name", "phone", mode="before")
    @classmethod
    def strip_profile_text(cls, value):
        if isinstance(value, str):
            value = " ".join(value.strip().split())
            return value or None
        return value


class AdminPasswordChange(BaseModel):
    current_password: str = Field(min_length=1, max_length=200)
    new_password: str = Field(min_length=8, max_length=200)
    confirm_password: str = Field(min_length=8, max_length=200)

    @model_validator(mode="after")
    def validate_match(self):
        if self.new_password != self.confirm_password:
            raise ValueError("New password and confirmation do not match.")
        if self.current_password == self.new_password:
            raise ValueError("New password must be different from the current password.")
        return self


class AdminSettingsPayload(BaseModel):
    project_name: str = Field(default="ONA Towers", max_length=120)
    sales_email: EmailStr | None = None
    sales_phone: str | None = Field(default=None, max_length=40)
    whatsapp_number: str | None = Field(default=None, max_length=40)
    response_sla_hours: int = Field(default=24, ge=1, le=168)
    timezone: str = Field(default="Africa/Dar_es_Salaam", max_length=80)
    customer_site_url: str = Field(default="/", max_length=500)
    notifications_enabled: bool = True


class AnalyticsPoint(BaseModel):
    label: str
    value: int


class TopPage(BaseModel):
    path: str
    visits: int


class AdminAnalytics(BaseModel):
    total_visits_30_days: int
    unique_sessions_30_days: int
    daily: list[AnalyticsPoint]
    monthly: list[AnalyticsPoint]
    top_pages: list[TopPage]


class AdminOverview(BaseModel):
    total_enquiries: int
    new_enquiries: int
    active_enquiries: int
    closed_enquiries: int
    enquiries_last_7_days: int
    active_team_members: int
    overdue_enquiries: int
    recent_enquiries: list[AdminEnquiry]
    settings: AdminSettingsPayload
    analytics: AdminAnalytics


class AdminSettingsRecord(BaseModel):
    settings: AdminSettingsPayload
    updated_at: datetime | None = None


class AdminEmailStatus(BaseModel):
    enabled: bool
    ready: bool
    provider: str
    from_configured: bool
    staff_recipient_configured: bool
    cityview_url_configured: bool
    cityview_url: str
    issues: list[str] = Field(default_factory=list)


class AdminEmailTestRequest(BaseModel):
    email: EmailStr


class AdminEmailTestResponse(BaseModel):
    success: bool = True
    provider: str
    message: str


class ApiMessage(BaseModel):
    success: bool = True
    message: str


class AdminMeResponse(BaseModel):
    user: AdminUser
