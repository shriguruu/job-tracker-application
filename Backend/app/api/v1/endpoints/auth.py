from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import AppException
from app.models.user import User
from app.schemas.user import UserSignup, UserLogin, AuthResponse, UserResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserSignup, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise AppException(
            status_code=status.HTTP_409_CONFLICT,
            code="EMAIL_EXISTS",
            message="An account with this email address already exists.",
        )

    user = User(
        user_name=user_in.user_name,
        email=user_in.email,
        password_hash=hash_password(user_in.password),
        phone_number=user_in.phone_number,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user_id=str(user.user_id), email=user.email)
    return AuthResponse(user_id=user.user_id, token=token)


@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def login(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise AppException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="INVALID_CREDENTIALS",
            message="Invalid email or password.",
        )

    token = create_access_token(user_id=str(user.user_id), email=user.email)
    return AuthResponse(user_id=user.user_id, token=token)


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
