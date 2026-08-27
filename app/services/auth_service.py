# 이메일 난수 생성 로직, 인증 시간(10분) 만료 검사, 인증 번호 일치 여부 검사, 
# 중복 검사 등 회원가입과 로그인에 필요한 비즈니스 로직을 담당하는 서비스 레이어.
# 작성자 : 엄인섭
import secrets
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.schemas.user import UserCreate
from app.crud import crud_user
from app.core.security import verify_password
from app.utils.email_sender import send_email 
from app.models.user import EmailVerification # 인증번호 저장용 모델(필요 시 생성)
from datetime import datetime, timedelta, timezone
from app.core.security import get_password_hash
from app.models.user import User
from app.core.enum.user import JoinStatus


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

    if user.join_status == JoinStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="가입 승인 대기 중입니다."
        )

    if user.join_status == JoinStatus.REJECTED.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="가입 신청이 거절되었습니다."
        )
        
    return user




# 1단계: 인증번호 요청 (요청 시 기존 인증번호 있으면 갱신)
async def request_password_reset(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="등록된 사용자가 아닙니다.")
    
    code = "".join([str(secrets.randbelow(10)) for _ in range(6)])
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    # 기존 인증 기록 확인 후 갱신 or 생성
    verif = db.query(EmailVerification).filter(EmailVerification.user_id == user.id).first()
    if verif:
        verif.verification_code = code
        verif.expires_at = expires_at
        verif.is_verified = False
    else:
        verif = EmailVerification(user_id=user.id, verification_code=code, expires_at=expires_at)
        db.add(verif)
    db.commit()
    
    # 이메일 발송 유틸리티 호출 (결과만 받아옴)
    success = await send_email(email, "비밀번호 재설정 인증번호", f"인증번호: {code}")
    
    # 결과가 False라면 API에서 에러 발생시키기
    if not success:
        raise HTTPException(status_code=500, detail="이메일 발송 서버에 문제가 발생했습니다. 잠시 후 다시 시도해주세요.")
    
    # [아키텍트 수정]: 프론트엔드 분기 처리를 위한 고유 식별 코드(AUTH_EMAIL_SENT) 추가
    return {
        "status": 200,
        "code": "AUTH_EMAIL_SENT"
    }

# 2단계: 인증번호 확인
def verify_code(db: Session, email: str, code: str):
    user = db.query(User).filter(User.email == email).first()
    
     # user가 None인지 확인
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    verif = db.query(EmailVerification).filter(EmailVerification.user_id == user.id).first()

    if not verif or verif.verification_code != code:
        raise HTTPException(status_code=400, detail="잘못된 인증번호입니다.")
    if verif.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="인증 시간이 만료되었습니다.")
    
    verif.is_verified = True # 인증 성공 상태 저장
    db.commit()
    
    # [아키텍트 수정]: 프론트엔드 분기 처리를 위한 고유 식별 코드(AUTH_VERIFIED_SUCCESS) 추가
    return {
        "status": 200,
        "code": "AUTH_VERIFIED_SUCCESS", 
    }

# 3단계: 비밀번호 변경
def reset_password(db: Session, email: str, new_password: str):
    user = db.query(User).filter(User.email == email).first()
    
    # user가 None인지 확인
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
        
    verif = db.query(EmailVerification).filter(EmailVerification.user_id == user.id).first()
    
    if not verif or not verif.is_verified:
        raise HTTPException(status_code=400, detail="인증이 완료되지 않았습니다.")
        
    user.password_hash = get_password_hash(new_password)
    db.delete(verif) # 인증 완료 후 데이터 삭제
    db.commit()
    
    # [아키텍트 수정]: 프론트엔드 분기 처리를 위한 고유 식별 코드(AUTH_PASSWORD_RESET_SUCCESS) 추가
    return {
        "status": 200,
        "code": "AUTH_PASSWORD_RESET_SUCCESS"
    }
