# 작성자 : 엄인섭 (2026-06-12)
# 학번/이메일 중복 검사 쿼리
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash # 보안 모듈에서 해시 함수를 가져옴

def get_user_by_student_id(db: Session, student_id: str):
    """학번으로 유저 조회 (중복 검사용)"""
    return db.query(User).filter(User.student_id == student_id).first()

def get_user_by_email(db: Session, email: str):
    """이메일로 유저 조회 (중복 검사용)"""
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user_in: UserCreate, default_role_id: int = 1):
    """새로운 유저 DB에 생성"""
    hashed_password = get_password_hash(user_in.password)
    
    db_user = User(
        student_id=user_in.student_id,
        email=user_in.email,
        password_hash=hashed_password,
        name=user_in.name,
        admission_year=user_in.admission_year,
        role_id=default_role_id, # 기본 역할 부여 (1 = 일반 회원 가정)
        status="재학",
        phone="010-0000-0000" # UI에 없으므로 기본값 세팅 (나중에 마이페이지에서 수정)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user