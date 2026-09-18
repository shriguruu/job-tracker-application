from app.schemas.user import UserSignup, UserLogin, AuthResponse, UserResponse
from app.schemas.resume import ResumeUploadResponse, ResumeDownloadResponse, ResumeResponse
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.schemas.error import ErrorResponse, ErrorDetail

__all__ = [
    "UserSignup",
    "UserLogin",
    "AuthResponse",
    "UserResponse",
    "ResumeUploadResponse",
    "ResumeDownloadResponse",
    "ResumeResponse",
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationResponse",
    "ErrorResponse",
    "ErrorDetail",
]
