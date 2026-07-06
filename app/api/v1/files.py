# 작성자 : 엄인섭
import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.crud import crud_file

router = APIRouter()
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@router.post("/upload", summary="파일 업로드")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 1. 파일 크기 검사
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="10MB 이하의 파일만 전송할 수 있습니다.")
    
    # 2. 파일 저장 (예시: 로컬 디렉토리 'uploads/')
    # 실제 환경에선 S3나 클라우드 스토리지를 권장합니다.
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    
    with open(file_path, "wb") as f:
        f.write(content)
        
    # 3. DB에 메타데이터 저장
    file_obj = crud_file.create_file(
        db, 
        url=file_path, 
        file_type=file.content_type, 
        size=len(content), 
        name=file.filename
    )
    
    return {"file_id": file_obj.id, "file_url": file_obj.file_url}