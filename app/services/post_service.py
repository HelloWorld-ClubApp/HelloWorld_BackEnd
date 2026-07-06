# 작성 권한 확인, 조회수 처리 로직

#작성자 : 천석훈 , 김세연, 문호성
#=============================
# app/services/post_service.py
from fastapi import HTTPException, status, UploadFile
from typing import List

# 1. 파일 규칙 검증 로직
def validate_image_file(file: UploadFile):
    """
    이미지 파일 규칙 검증
    - 10MB 이하 제한
    - 허용 확장자: jpg, png, pdf
    """
    # 10MB 제한 (10 * 1024 * 1024 bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024
    allowed_extensions = [".jpg", ".png", ".pdf"]
    
    # 파일 크기 확인
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="허용하지않는 이미지 규칙입니다")
    
    # 확장자 확인
    if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        raise HTTPException(status_code=400, detail="허용하지않는 이미지 규칙입니다")

# 2. 자유게시판 작성 제한 검사
def check_free_post_limit(db, user_id: int):
    """자유게시판 글 작성 5개 제한 확인"""
    from app.crud.crud_post import get_user_post_count
    
    if get_user_post_count(db, user_id, "일반") >= 5:
        raise HTTPException(status_code=400, detail="일반은 최대 5개까지만 작성 가능합니다.")

# 3. 수정/삭제 권한 체크
def check_post_permission(current_user, post, is_delete: bool = False):
    """
    본인 확인 및 관리자 권한 체크
    - 본인: 수정/삭제 가능
    - 관리자: 삭제만 가능 (관리자 role_id=2 가정)
    """
    # 본인 확인
    if post.user_id == current_user.id:
        return True
    
    # 관리자 확인 (삭제일 때만 가능)
    if is_delete and getattr(current_user, 'role_id', None) == 2:
        return True
        
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, 
        detail="권한이 없습니다."
    )

# 4. 질문게시판 작성 제한 검사
def check_question_post_limit(db, user_id: int):
    """
    [Post_003] 질문게시판 글 작성 5개 제한 확인
    """
    from app.crud.crud_post import get_user_post_count
    
    if get_user_post_count(db, user_id, "질문") >= 5:
        raise HTTPException(status_code=400, detail="질문게시판은 최대 5개까지만 작성 가능합니다.")