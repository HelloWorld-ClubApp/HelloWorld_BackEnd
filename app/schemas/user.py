# 작성자 : 엄인섭
import re
from pydantic import BaseModel, EmailStr, Field, model_validator

# 회원가입 입력 형식(8~20자 제한, 이메일 정규식 등)
class UserCreate(BaseModel):
    student_id: str = Field(..., min_length=10, max_length=15, description="학번")
    password: str = Field(..., min_length=8, max_length=19, description="비밀번호 (8자 이상 20자 미만)")
    password_confirm: str = Field(..., min_length=8, max_length=19, description="비밀번호 확인")
    email: EmailStr = Field(..., description="이메일")
    name: str = Field(..., min_length=2, max_length=10, description="본명")
    admission_year: int = Field(..., description="학교 입학년도 (예: 2024)")

    # Pydantic v2 방식: 비밀번호 일치 여부 검증
    @model_validator(mode='after')
    def validate_password_rules(self) -> 'UserCreate':
        # 1. 일치 여부 검사
        if self.password != self.password_confirm:
            raise ValueError('비밀번호가 일치하지 않습니다.')
            
        # 2. 정규식 검사
        pattern = r"^(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).+$"
        if not re.match(pattern, self.password):
            raise ValueError("잘못된 비밀번호 형식입니다. (소문자, 숫자, 특수문자 포함)")
            
        return self

class UserResponse(BaseModel):
    id: int
    student_id: str
    email: str
    name: str
    admission_year: int
    status: str

    class Config:
        from_attributes = True
        
        
        
# 로그인 입력 형식 (학번과 비밀번호) 및 JWT 토큰 응답 형식
class UserLogin(BaseModel):
    student_id: str = Field(..., description="로그인할 학번")
    password: str = Field(..., description="비밀번호")


# ==========================================
# 3. 비밀번호 찾기 (이메일 인증) 스키마
# ==========================================
class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(..., description="가입 시 등록한 이메일")

class PasswordResetVerify(BaseModel):
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, description="6자리 인증번호")

class PasswordResetConfirm(BaseModel):
    email: EmailStr
    code: str = Field(..., description="인증 완료된 코드")
    new_password: str = Field(..., min_length=8, max_length=19, description="새 비밀번호")
    new_password_confirm: str = Field(..., min_length=8, max_length=19, description="새 비밀번호 확인")

    @model_validator(mode='after')
    def validate_password_rules(self) -> 'PasswordResetConfirm':
        # 1. 비밀번호 일치 확인
        if self.new_password != self.new_password_confirm:
            raise ValueError("비밀번호가 일치하지 않습니다.")
        
        # 2. 정규식 규칙: 소문자, 숫자, 특수문자 포함
        pattern = r"^(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).+$"
        if not re.match(pattern, self.new_password):
            raise ValueError("잘못된 비밀번호 형식입니다.")
            
        return self