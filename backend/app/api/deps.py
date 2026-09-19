import uuid
from fastapi import Depends, Header
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_access_token
from app.core.exceptions import AppException
from app.models.user import User


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization:
        raise AppException(
            status_code=401,
            code="UNAUTHORIZED",
            message="Authorization header is required.",
        )

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AppException(
            status_code=401,
            code="INVALID_AUTH_HEADER",
            message="Authorization header must be in format 'Bearer <token>'.",
        )

    token = parts[1]
    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AppException(
            status_code=401,
            code="INVALID_TOKEN",
            message="Token payload is missing user ID.",
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise AppException(
            status_code=401,
            code="INVALID_TOKEN",
            message="Invalid user ID format in token.",
        )

    user = db.query(User).filter(User.user_id == user_uuid).first()
    if not user:
        raise AppException(
            status_code=401,
            code="USER_NOT_FOUND",
            message="User associated with this token no longer exists.",
        )

    return user
