from datetime import datetime
import uuid
from pydantic import BaseModel


class ResumeUploadResponse(BaseModel):
    resume_id: uuid.UUID
    resume_name: str

    model_config = {"from_attributes": True}


class ResumeDownloadResponse(BaseModel):
    url: str
    expires_in: int


class ResumeResponse(BaseModel):
    resume_id: uuid.UUID
    user_id: uuid.UUID
    resume_name: str
    resume_key: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
