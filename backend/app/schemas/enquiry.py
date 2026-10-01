from datetime import datetime
from enum import Enum
import re
from pydantic import BaseModel, EmailStr, Field, field_validator


class EnquiryType(str, Enum):
    enquire_about_residence = "enquire_about_residence"
    request_floor_plans = "request_floor_plans"
    schedule_viewing = "schedule_viewing"
    talk_to_sales = "talk_to_sales"
    general = "general"


class EnquiryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=7, max_length=30)
    email: EmailStr | None = None
    residence_interest: str | None = Field(default=None, max_length=120)
    enquiry_type: EnquiryType = EnquiryType.general
    message: str | None = Field(default=None, max_length=2000)
    consent: bool
    source: str = Field(default="website", max_length=100)

    # Honeypot: frontend must leave blank.
    company_website: str = Field(default="", max_length=250)

    @field_validator("name", "residence_interest", "source", mode="before")
    @classmethod
    def normalize_text(cls, value):
        if isinstance(value, str):
            return " ".join(value.strip().split())
        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str):
        value = value.strip()
        if not re.fullmatch(r"[+()\-\s0-9]{7,30}", value):
            raise ValueError("Phone number contains invalid characters")
        digits = re.sub(r"\D", "", value)
        if len(digits) < 7 or len(digits) > 15:
            raise ValueError("Phone number must contain 7 to 15 digits")
        return value

    @field_validator("consent")
    @classmethod
    def consent_required(cls, value: bool):
        if value is not True:
            raise ValueError("Consent is required")
        return value


class EnquiryRecord(BaseModel):
    id: str
    reference_number: str
    name: str
    phone: str
    email: EmailStr | None = None
    residence_interest: str | None = None
    enquiry_type: EnquiryType
    message: str | None = None
    consent: bool
    source: str
    status: str = "new"
    created_at: datetime


class EnquiryCreated(BaseModel):
    success: bool = True
    reference_number: str
    message: str = "Thank you. Your enquiry has been received."
    customer_email_sent: bool = False
    staff_email_sent: bool = False
