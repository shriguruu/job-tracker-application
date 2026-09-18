from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session, joinedload
from app.core.database import get_db
from app.core.exceptions import AppException
from app.models.application import Application, ApplicationStatus
from app.models.resume import Resume
from app.models.user import User
from app.schemas.application import ApplicationCreate, ApplicationUpdate, ApplicationResponse
from app.api.deps import get_current_user

router = APIRouter(prefix="/applications", tags=["Applications"])


def to_response_dto(app_obj: Application) -> ApplicationResponse:
    resume_name = app_obj.resume.resume_name if app_obj.resume else None
    return ApplicationResponse(
        application_id=app_obj.application_id,
        user_id=app_obj.user_id,
        resume_id=app_obj.resume_id,
        company_name=app_obj.company_name,
        role_name=app_obj.role_name,
        ctc_amount=app_obj.ctc_amount,
        ctc_currency=app_obj.ctc_currency,
        status=app_obj.status,
        job_description_url=app_obj.job_description_url,
        notes=app_obj.notes,
        created_at=app_obj.created_at,
        updated_at=app_obj.updated_at,
        resume_name=resume_name,
    )


@router.get("", response_model=List[ApplicationResponse], status_code=status.HTTP_200_OK)
def get_applications(
    status_filter: Optional[ApplicationStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Application)
        .options(joinedload(Application.resume))
        .filter(Application.user_id == current_user.user_id)
    )

    if status_filter:
        query = query.filter(Application.status == status_filter)

    query = query.order_by(Application.created_at.desc())
    offset = (page - 1) * page_size
    applications = query.offset(offset).limit(page_size).all()

    return [to_response_dto(app) for app in applications]


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
def create_application(
    app_in: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate resume ownership if resume_id is provided
    if app_in.resume_id:
        resume = (
            db.query(Resume)
            .filter(Resume.resume_id == app_in.resume_id, Resume.user_id == current_user.user_id)
            .first()
        )
        if not resume:
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                code="INVALID_RESUME",
                message="The specified resume was not found or does not belong to your account.",
            )

    new_app = Application(
        user_id=current_user.user_id,
        company_name=app_in.company_name,
        role_name=app_in.role_name,
        ctc_amount=app_in.ctc_amount,
        ctc_currency=app_in.ctc_currency,
        status=app_in.status,
        job_description_url=app_in.job_description_url,
        notes=app_in.notes,
        resume_id=app_in.resume_id,
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)

    # Re-fetch with joined resume
    app_with_resume = (
        db.query(Application)
        .options(joinedload(Application.resume))
        .filter(Application.application_id == new_app.application_id)
        .first()
    )
    return to_response_dto(app_with_resume)


@router.get("/{id}", response_model=ApplicationResponse, status_code=status.HTTP_200_OK)
def get_application(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app_obj = (
        db.query(Application)
        .options(joinedload(Application.resume))
        .filter(Application.application_id == id, Application.user_id == current_user.user_id)
        .first()
    )
    if not app_obj:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="APPLICATION_NOT_FOUND",
            message=f"Application with ID {id} was not found.",
        )
    return to_response_dto(app_obj)


@router.put("/{id}", response_model=ApplicationResponse, status_code=status.HTTP_200_OK)
def update_application(
    id: uuid.UUID,
    app_update: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app_obj = (
        db.query(Application)
        .filter(Application.application_id == id, Application.user_id == current_user.user_id)
        .first()
    )
    if not app_obj:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="APPLICATION_NOT_FOUND",
            message=f"Application with ID {id} was not found.",
        )

    # If updating resume_id, validate ownership
    update_dict = app_update.model_dump(exclude_unset=True)
    if "resume_id" in update_dict and update_dict["resume_id"] is not None:
        resume = (
            db.query(Resume)
            .filter(Resume.resume_id == update_dict["resume_id"], Resume.user_id == current_user.user_id)
            .first()
        )
        if not resume:
            raise AppException(
                status_code=status.HTTP_400_BAD_REQUEST,
                code="INVALID_RESUME",
                message="The specified resume was not found or does not belong to your account.",
            )

    for key, value in update_dict.items():
        setattr(app_obj, key, value)

    db.commit()
    db.refresh(app_obj)

    app_with_resume = (
        db.query(Application)
        .options(joinedload(Application.resume))
        .filter(Application.application_id == app_obj.application_id)
        .first()
    )
    return to_response_dto(app_with_resume)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    app_obj = (
        db.query(Application)
        .filter(Application.application_id == id, Application.user_id == current_user.user_id)
        .first()
    )
    if not app_obj:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="APPLICATION_NOT_FOUND",
            message=f"Application with ID {id} was not found.",
        )

    db.delete(app_obj)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
