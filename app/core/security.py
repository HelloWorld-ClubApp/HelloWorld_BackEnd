# 비밀번호 해싱(bcrypt), JWT 토큰 발급 및 검증
# 작성자 : 엄인섭 (2026-06-12)
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

def get_password_hash(password: str) -> str:
    """
    평문 비밀번호를 bcrypt를 사용하여 해싱합니다.
    """
    # 1. 문자열을 바이트로 변환
    pwd_bytes = password.encode('utf-8')
    
    # 2. 소금(salt)을 치고 해싱
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(pwd_bytes, salt)
    
    # 3. 데이터베이스에 저장하기 위해 문자열로 변환하여 리턴
    return hashed_pwd.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    입력받은 비밀번호와 DB의 해시 비밀번호가 일치하는지 검증합니다.
    """
    plain_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    # bcrypt의 checkpw 함수를 사용하여 검증
    return bcrypt.checkpw(plain_bytes, hashed_bytes)

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """JWT 토큰 생성"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)
        
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt