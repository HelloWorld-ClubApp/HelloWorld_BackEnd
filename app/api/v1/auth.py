# 회원가입, 로그인, 이메일 인증 (User_001~005)
# 작성자 : 엄인섭
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.schemas.user import UserCreate, UserResponse, UserLogin, PasswordResetRequest, PasswordResetVerify, PasswordResetConfirm
from app.schemas.token import Token
from app.services import auth_service
from app.core import security

router = APIRouter()

# User_001: 회원가입 API (POST /api/v1/auth/signup)
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """
    회원가입 API
    - 프론트엔드 UI의 학번, 이메일, 비밀번호, 이름, 입학년도를 전달받아 계정을 생성합니다.
    """
    return auth_service.register_new_user(db, user_in)



@router.post("/login", response_model=Token) # 반환 형식을 명시적인 Token 스키마로 지정
def login(login_in: UserLogin, db: Session = Depends(get_db)): # OAuth2 폼 대신 UserLogin 스키마 사용
    """
    로그인 API (JSON 데이터 수신)
    - Postman에서 Body -> raw -> JSON으로 학번과 비밀번호를 전송합니다.
    - 성공 시 JWT Access Token을 반환합니다.
    """
    # login_in.student_id와 login_in.password로 안전하게 데이터 접근
    user = auth_service.authenticate_user(db, student_id=login_in.student_id, password=login_in.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="학번 또는 비밀번호가 일치하지 않습니다.",
        )
    
    # 토큰 생성 및 반환 (Pydantic이 자동으로 Token 모델 형식에 맞게 변환해줍니다)
    access_token = security.create_access_token(data={"sub": user.student_id})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/password-reset/request")
async def request_reset(req: PasswordResetRequest, db: Session = Depends(get_db)):
    return await auth_service.request_password_reset(db, req.email)

@router.post("/password-reset/verify")
def verify_reset(req: PasswordResetVerify, db: Session = Depends(get_db)):
    return auth_service.verify_code(db, req.email, req.code)

@router.post("/password-reset/confirm")
def confirm_reset(req: PasswordResetConfirm, db: Session = Depends(get_db)):
    return auth_service.reset_password(db, req.email, req.new_password)