# 파일 용량 검증 및 로컬 업로드 로직
# 작성자 : 천석훈, 김세연, 문호성, 강기민
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.core.file_paths import (
    MAX_UPLOAD_SIZE,
    UPLOAD_DIR,
    build_upload_url,
    ensure_upload_dir,
)
from app.models.file import File

# 허용하는 확장자 규칙
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

def validate_and_upload_profile_image(db: Session, file: UploadFile) -> int:
    """
    [MY_001] 프로필 이미지 검증 및 저장 후 DB의 file_id를 반환합니다.
    - 확장자 검증 (JPG, PNG)
    - 파일 용량 검증
    """
    # 1. 파일 확장자 검증
    # 파일 이름(예: profile.png)에서 맨 뒤의 확장자만 소문자로 추출
    original_name = Path(file.filename or "profile").name
    file_extension = Path(original_name).suffix.lstrip(".").lower()
    
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="허용하지않는 이미지 규칙입니다"
        )
        
    # 2. 파일 용량(크기) 검증
    # 파일 데이터를 끝까지 읽어보고(seek) 위치(tell)를 통해 실제 용량을 계산!
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)  # 용량만 재고 다시 저장을 위해 파일의 처음으로 커서 복귀

    if file_size > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="20MB 이하의 이미지만 전송할 수 있습니다."
        )

    ensure_upload_dir()
    stored_name = f"{uuid4().hex}{Path(original_name).suffix}"
    file_path = Path(UPLOAD_DIR) / stored_name
    file_url = build_upload_url(stored_name)

    content = file.file.read()
    file.file.seek(0)

    with file_path.open("wb") as upload_file:
        upload_file.write(content)

    # 4. 데이터베이스 'files' 테이블에 방금 검증한 파일 정보 등록
    new_file = File(
        file_url=file_url,
        file_type=file.content_type or f"image/{file_extension}",
        file_size=file_size,
        original_name=original_name
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    
    # 방금 DB에 저장되면서 생성된 파일의 고유번호(PK)를 반환!
    return new_file.id
