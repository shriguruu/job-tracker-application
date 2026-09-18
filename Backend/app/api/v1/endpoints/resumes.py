import os
from typing import List
import uuid
from fastapi import APIRouter, Depends, File, Form, Response, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AppException
from app.models.resume import Resume
from app.models.user import User
from app.schemas.resume import ResumeResponse, ResumeUploadResponse, ResumeDownloadResponse
from app.services.s3 import s3_service
from app.api.deps import get_current_user

router = APIRouter(prefix="/resumes", tags=["Resumes"])


@router.get("", response_model=List[ResumeResponse], status_code=status.HTTP_200_OK)
def list_resumes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.user_id)
        .order_by(Resume.created_at.desc())
        .all()
    )
    return resumes


@router.post("", response_model=ResumeUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    resume_name: str = Form(..., min_length=1, max_length=150),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Validate file extension and MIME type
    if not file.filename.lower().endswith(".pdf") or (
        file.content_type and "pdf" not in file.content_type.lower()
    ):
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="INVALID_FILE_TYPE",
            message="Only PDF documents (.pdf) are allowed.",
        )

    # 2. Validate file size (max 5MB)
    content = await file.read()
    if len(content) > settings.MAX_RESUME_SIZE_BYTES:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="FILE_TOO_LARGE",
            message=f"File size exceeds the limit of {settings.MAX_RESUME_SIZE_BYTES // (1024 * 1024)}MB.",
        )
    if len(content) == 0:
        raise AppException(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="EMPTY_FILE",
            message="Uploaded file is empty.",
        )

    # Reset cursor for streaming / uploading
    await file.seek(0)

    # 3. Generate key and upload to S3 before DB insertion
    resume_id = uuid.uuid4()
    object_key = f"resumes/{current_user.user_id}/{resume_id}.pdf"

    try:
        s3_service.upload_file(
            file_obj=file.file,
            object_key=object_key,
            content_type="application/pdf",
        )
    except Exception as e:
        raise AppException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="STORAGE_UPLOAD_ERROR",
            message=f"Failed to upload resume to storage: {str(e)}",
        )

    # 4. Insert into database only after S3 upload succeeds
    resume = Resume(
        resume_id=resume_id,
        user_id=current_user.user_id,
        resume_name=resume_name.strip(),
        resume_key=object_key,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)

    return ResumeUploadResponse(resume_id=resume.resume_id, resume_name=resume.resume_name)


@router.get("/{id}/download-url", response_model=ResumeDownloadResponse, status_code=status.HTTP_200_OK)
def get_resume_download_url(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.resume_id == id, Resume.user_id == current_user.user_id)
        .first()
    )
    if not resume:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="RESUME_NOT_FOUND",
            message=f"Resume with ID {id} was not found.",
        )

    url = s3_service.generate_presigned_url(
        object_key=resume.resume_key,
        expires_in=settings.PRESIGNED_URL_EXPIRE_SECONDS,
    )
    return ResumeDownloadResponse(
        url=url,
        expires_in=settings.PRESIGNED_URL_EXPIRE_SECONDS,
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    resume = (
        db.query(Resume)
        .filter(Resume.resume_id == id, Resume.user_id == current_user.user_id)
        .first()
    )
    if not resume:
        raise AppException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="RESUME_NOT_FOUND",
            message=f"Resume with ID {id} was not found.",
        )

    # Delete object from S3
    s3_service.delete_file(resume.resume_key)

    # Note: DB foreign keys in applications will SET NULL automatically
    db.delete(resume)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/mock-download/{object_key:path}")
def mock_download(object_key: str):
    """Local mock helper to allow testing file downloads when running locally without AWS."""
    local_dir = getattr(s3_service, "_local_storage_dir", None)
    if not local_dir:
        raise AppException(status_code=404, code="NOT_FOUND", message="Local storage not found")
    file_path = os.path.join(local_dir, object_key.replace("/", os.sep))
    if not os.path.exists(file_path):
        raise AppException(status_code=404, code="FILE_NOT_FOUND", message="File does not exist")
    return FileResponse(file_path, media_type="application/pdf", filename=os.path.basename(file_path))
