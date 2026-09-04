from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.file_paths import MAX_UPLOAD_SIZE, UPLOAD_DIR, UPLOAD_URL_PREFIX
from app.crud import crud_file
from app.services import storage_service


router = APIRouter()


def resolve_upload_path(file_url: str) -> Path:
    upload_root = Path(UPLOAD_DIR).resolve()
    normalized_url = file_url.replace("\\", "/").lstrip("/")
    upload_prefix = UPLOAD_URL_PREFIX.lstrip("/") + "/"
    relative_path = (
        normalized_url[len(upload_prefix):]
        if normalized_url.startswith(upload_prefix)
        else Path(normalized_url).name
    )
    file_path = Path(UPLOAD_DIR) / relative_path
    resolved_path = file_path.resolve()

    if resolved_path != upload_root and upload_root not in resolved_path.parents:
        raise HTTPException(status_code=400, detail="Invalid file path.")

    return resolved_path


@router.post("/upload", summary="Upload file")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail="Files up to 20MB are allowed.")

    original_name = storage_service.get_original_name(file.filename)
    file_type = file.content_type or "application/octet-stream"
    stored_file = storage_service.upload_bytes_to_storage(
        content=content,
        original_name=original_name,
        content_type=file_type,
        folder="uploads",
    )

    file_obj = crud_file.create_file(
        db,
        url=stored_file.file_url,
        file_type=file_type,
        size=len(content),
        name=original_name,
    )

    base_url = str(request.base_url).rstrip("/")
    file_absolute_url = (
        file_obj.file_url
        if storage_service.is_remote_file_url(file_obj.file_url)
        else f"{base_url}{file_obj.file_url}"
    )
    return {
        "file_id": file_obj.id,
        "file_url": file_obj.file_url,
        "file_absolute_url": file_absolute_url,
        "download_url": f"/api/v1/files/{file_obj.id}/download",
        "download_absolute_url": f"{base_url}/api/v1/files/{file_obj.id}/download",
    }


@router.get("/{file_id}/download", summary="Download file")
def download_file(file_id: int, db: Session = Depends(get_db)):
    file_obj = crud_file.get_file_by_id(db, file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="File not found.")

    if storage_service.is_remote_file_url(file_obj.file_url):
        return RedirectResponse(
            url=storage_service.add_download_query(
                file_obj.file_url,
                file_obj.original_name,
            )
        )

    file_path = resolve_upload_path(file_obj.file_url)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File does not exist on server.")

    return FileResponse(
        path=file_path,
        media_type=file_obj.file_type,
        filename=file_obj.original_name,
    )
