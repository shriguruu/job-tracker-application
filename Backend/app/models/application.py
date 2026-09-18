import enum
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Numeric, Text, Enum, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.guid import GUID


class ApplicationStatus(str, enum.Enum):
    APPLIED = "applied"
    OA = "oa"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


class Application(Base):
    __tablename__ = "applications"

    application_id = Column(GUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(GUID, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    resume_id = Column(GUID, ForeignKey("resumes.resume_id", ondelete="SET NULL"), nullable=True, index=True)
    company_name = Column(String(150), nullable=False)
    role_name = Column(String(150), nullable=False)
    ctc_amount = Column(Numeric(12, 2), nullable=True)
    ctc_currency = Column(String(3), nullable=False, default="INR")
    status = Column(
        Enum(
            ApplicationStatus,
            name="application_status",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=ApplicationStatus.APPLIED,
    )
    job_description_url = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    user = relationship("User", back_populates="applications")
    resume = relationship("Resume", back_populates="applications")
