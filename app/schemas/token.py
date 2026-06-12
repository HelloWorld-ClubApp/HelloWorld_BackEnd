# JWT 토큰 응답 포맷
from pydantic import BaseModel, Field
from typing import Optional

class Token(BaseModel):
    """
    로그인 성공 시 클라이언트에게 반환되는 토큰 응답 포맷
    """
    access_token: str = Field(..., description="JWT 엑세스 토큰")
    token_type: str = Field("bearer", description="토큰 타입")

class TokenPayload(BaseModel):
    """
    JWT 토큰을 디코딩했을 때 나오는 내용물 (Payload)
    """
    sub: Optional[str] = None # 토큰 주인의 식별자 (여기서는 학번)