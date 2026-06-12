# 작성자 : 엄인섭
from pydantic import BaseModel, EmailStr, Field, model_validator

# 회원가입 입력 형식(8~20자 제한, 이메일 정규식 등)
class UserCreate(BaseModel):
    student_id: str = Field(..., min_length=10, max_length=15, description="학번")
    password: str = Field(..., min_length=8, max_length=19, description="비밀번호 (8자 이상 20자 이하)")
    password_confirm: str = Field(..., min_length=8, max_length=20, description="비밀번호 확인")
    email: EmailStr = Field(..., description="이메일")
    name: str = Field(..., min_length=2, max_length=10, description="본명")
    admission_year: int = Field(..., description="학교 입학년도 (예: 2024)")

    # Pydantic v2 방식: 비밀번호 일치 여부 검증
    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserCreate':
        if self.password != self.password_confirm:
            raise ValueError('비밀번호가 일치하지 않습니다.')
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

class Token(BaseModel):
    access_token: str = Field(..., description="JWT 엑세스 토큰")
    token_type: str = Field("bearer", description="토큰 타입")