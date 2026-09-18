from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid
from pydantic import BaseModel, Field
from app.models.application import ApplicationStatus


class ApplicationBase(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=150)
    role_name: str = Field(..., min_length=1, max_length=150)
    ctc_amount: Optional[Decimal] = None
    ctc_currency: str = Field("INR", min_length=3, max_length=3)
    status: ApplicationStatus = ApplicationStatus.APPLIED
    job_description_url: Optional[str] = None
    notes: Optional[str] = None
    resume_id: Optional[uuid.UUID] = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company_name: Optional[str] = Field(None, min_length=1, max_length=150)
    role_name: Optional[str] = Field(None, min_length=1, max_length=150)
    ctc_amount: Optional[Decimal] = None
    ctc_currency: Optional[str] = Field(None, min_length=3, max_length=3)
    status: Optional[ApplicationStatus] = None
    job_description_url: Optional[str] = None
    notes: Optional[str] = None
    resume_id: Optional[uuid.UUID] = None


class ApplicationResponse(BaseModel):
    application_id: uuid.UUID
    user_id: uuid.UUID
    resume_id: Optional[uuid.UUID] = None
    company_name: str
    role_name: str
    ctc_amount: Optional[Decimal] = None
    ctc_currency: str
    status: ApplicationStatus
    job_description_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    resume_name: Optional[str] = None

    model_config = {"from_attributes": True}
