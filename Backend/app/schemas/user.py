from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, Field, field_validator


class UserSignup(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    phone_number: Optional[str] = Field(None, max_length=20)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower().strip()


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator("email")
    @classmethod
    def lowercase_email(cls, v: str) -> str:
        return v.lower().strip()


class AuthResponse(BaseModel):
    user_id: uuid.UUID
    token: str


class UserResponse(BaseModel):
    user_id: uuid.UUID
    user_name: str
    email: str
    phone_number: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}
