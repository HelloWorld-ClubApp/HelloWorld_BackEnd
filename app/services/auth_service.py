# 이메일 난수 생성 로직, 인증 시간(10분) 만료 검사, 인증 번호 일치 여부 검사, 
# 중복 검사 등 회원가입과 로그인에 필요한 비즈니스 로직을 담당하는 서비스 레이어.
# 작성자 : 엄인섭
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.user import UserCreate
from app.crud import crud_user
from app.core.security import verify_password

def register_new_user(db: Session, user_in: UserCreate):
    """
    회원가입 비즈니스 로직
    - 중복 검사를 통과한 유저만 DB에 저장하도록 CRUD로 넘깁니다.
    """
    
    # 1. 학번 중복 검사
    user_by_student_id = crud_user.get_user_by_student_id(db, student_id=user_in.student_id)
    if user_by_student_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 가입된 학번입니다."
        )
        
    # 2. 이메일 중복 검사
    user_by_email = crud_user.get_user_by_email(db, email=user_in.email)
    if user_by_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 이메일입니다."
        )
 
    # 3. 모든 검증을 통과했으므로 유저 생성 (내부적으로 get_password_hash 호출됨)
    return crud_user.create_user(db=db, user_in=user_in)

def authenticate_user(db: Session, student_id: str, password: str):
    """
    학번과 비밀번호를 검증하여 로그인 성공 시 유저 객체를 반환합니다.
    """
    user = crud_user.get_user_by_student_id(db, student_id=student_id)
    if not user:
        return False # 학번이 존재하지 않음
        
    if not verify_password(password, user.password_hash):
        return False # 비밀번호가 틀림
        
    return user