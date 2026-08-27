# 작성자 : 엄인섭
import os
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import crud_file

router = APIRouter()
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_DIR = "uploads"

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
        "file_absolute_url": f"{base_url}{file_obj.file_url}"
    }
