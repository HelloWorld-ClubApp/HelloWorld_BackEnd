# 작성자 : 엄인섭
import os
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import crud_file

router = APIRouter()
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = "uploads"


def resolve_upload_path(file_url: str) -> Path:
    upload_root = Path(UPLOAD_DIR).resolve()
    normalized_url = file_url.replace("\\", "/").lstrip("/")
    candidate = Path(normalized_url)
    file_path = candidate if candidate.parts and candidate.parts[0] == UPLOAD_DIR else Path(UPLOAD_DIR) / candidate.name
    resolved_path = file_path.resolve()

    if resolved_path != upload_root and upload_root not in resolved_path.parents:
        raise HTTPException(status_code=400, detail="잘못된 파일 경로입니다.")

    return resolved_path

@router.post("/upload", summary="파일 업로드")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. 파일 크기 검사
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="10MB 이하의 파일만 전송할 수 있습니다.")
    
    # 2. 파일 저장 (예시: 로컬 디렉토리 'uploads/')
    # 실제 환경에선 S3나 클라우드 스토리지를 권장합니다.
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    original_name = Path(file.filename or "upload").name
    stored_name = f"{uuid4().hex}{Path(original_name).suffix}"
    file_path = os.path.join(UPLOAD_DIR, stored_name)
    file_url = f"/uploads/{stored_name}"
    file_type = file.content_type or "application/octet-stream"
    
    with open(file_path, "wb") as f:
        f.write(content)
        
    # 3. DB에 메타데이터 저장
    file_obj = crud_file.create_file(
        db,
        url=file_url,
        file_type=file_type,
        size=len(content),
        name=original_name
    )
    
    base_url = str(request.base_url).rstrip("/")
    return {
        "file_id": file_obj.id,
        "file_url": file_obj.file_url,
        "file_absolute_url": f"{base_url}{file_obj.file_url}",
        "download_url": f"/api/v1/files/{file_obj.id}/download",
        "download_absolute_url": f"{base_url}/api/v1/files/{file_obj.id}/download"
    }


@router.get("/{file_id}/download", summary="파일 다운로드")
def download_file(file_id: int, db: Session = Depends(get_db)):
    file_obj = crud_file.get_file_by_id(db, file_id)
    if not file_obj:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다.")

    file_path = resolve_upload_path(file_obj.file_url)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="파일이 서버에 존재하지 않습니다.")

    return FileResponse(
        path=file_path,
        media_type=file_obj.file_type,
        filename=file_obj.original_name,
    )
