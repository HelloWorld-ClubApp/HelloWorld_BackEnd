from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.file_paths import MAX_UPLOAD_SIZE
from app.models.file import File
from app.services import storage_service


ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}


def validate_image_upload(file: UploadFile, content: bytes) -> tuple[str, str]:
    original_name = storage_service.get_original_name(file.filename, fallback="profile")
    file_extension = Path(original_name).suffix.lstrip(".").lower()

    if file_extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only jpg, jpeg, and png images can be uploaded.",
        )

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Images up to 20MB are allowed.",
        )

    return original_name, file.content_type or f"image/{file_extension}"


def validate_and_upload_profile_image(db: Session, file: UploadFile) -> int:
    content = file.file.read()
    file.file.seek(0)
    original_name, file_type = validate_image_upload(file, content)

    stored_file = storage_service.upload_bytes_to_storage(
        content=content,
        original_name=original_name,
        content_type=file_type,
        folder="profiles",
    )

    new_file = File(
        file_url=stored_file.file_url,
        file_type=file_type,
        file_size=len(content),
        original_name=original_name,
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)

    return new_file.id
