# 비밀번호를 검증하고 탈퇴 처리를 수행하는 핵심 로직
# 작성자 : 엄인섭
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud import crud_user
from app.models.user import User
from app.core.security import verify_password

def withdraw_user_account(db: Session, current_user: User, password_input: str):
    """
    [MY_007] 회원탈퇴 비즈니스 로직
    - 현재 비밀번호 일치 여부를 검증하고, 성공 시 Soft Delete를 수행합니다.
    """
    # 1. 입력받은 평문 비밀번호와 DB의 해시된 비밀번호 비교
    if not verify_password(password_input, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호가 일치하지 않습니다."
        )
    
    # 2. 비밀번호가 일치하면 Soft Delete 수행
    crud_user.soft_delete_user(db, current_user.id)
    
    return {"message": "회원탈퇴가 성공적으로 처리되었습니다."}