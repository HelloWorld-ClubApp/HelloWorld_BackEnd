# 파일 용량(10MB) 검증 및 S3 업로드 로직
# 작성자 : 천석훈, 김세연, 문호성, 강기민
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from app.models.file import File

# 10MB 용량 제한 (바이트 단위 계산: 10 * 1024 * 1024)
MAX_FILE_SIZE = 10 * 1024 * 1024
# 허용하는 확장자 규칙
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

def validate_and_upload_profile_image(db: Session, file: UploadFile) -> int:
    """
    [MY_001] 프로필 이미지 검증 및 저장 후 DB의 file_id를 반환합니다.
    - 확장자 검증 (JPG, PNG)
    - 파일 용량 검증 (10MB 이하)
    """
    # 1. 파일 확장자 검증
    # 파일 이름(예: profile.png)에서 맨 뒤의 확장자만 소문자로 추출
    file_extension = file.filename.split('.')[-1].lower() if '.' in file.filename else ""
    
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
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="허용하지않는 이미지 규칙입니다"
        )
        
    # 3. 실제 파일 저장 로직 (현재는 S3 연동 전이므로 가상 URL 세팅)
    # TODO: 프론트엔드 연동 테스트 후, 이곳에 진짜 AWS S3 업로드 코드를 추가하세요!
    fake_file_url = f"https://s3.example.com/profiles/{file.filename}"
    
    # 4. 데이터베이스 'files' 테이블에 방금 검증한 파일 정보 등록
    new_file = File(
        file_url=fake_file_url,
        file_type=file_extension,
        file_size=file_size,
        original_name=file.filename
    )
    db.add(new_file)
    db.commit()
    db.refresh(new_file)
    
    # 방금 DB에 저장되면서 생성된 파일의 고유번호(PK)를 반환!
    return new_file.id