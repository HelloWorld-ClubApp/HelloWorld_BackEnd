# 공통 의존성 주입 (get_db, get_current_user 등)
# 작성자 : 엄인섭 (2026-06-12)
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import InvalidTokenError
from app.core.database import SessionLocal
from app.core.config import settings
from app.crud import crud_user

# 토큰을 받을 API 주소 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_db():
    """DB 세션을 생성하고 요청이 끝나면 닫아줍니다."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    요청 헤더의 JWT 토큰을 해독하여 현재 로그인한 유저 객체를 반환합니다.
    어떤 API든 인자에 Depends(get_current_user)만 넣으면 로그인 검증이 끝납니다.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보를 확인할 수 없거나 토큰이 만료되었습니다.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 토큰 해독
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        student_id: str | None = payload.get("sub")
        if student_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception

    # DB에서 유저 확인
    user = crud_user.get_user_by_student_id(db, student_id=student_id)
    if user is None:
        raise credentials_exception
        
    return user