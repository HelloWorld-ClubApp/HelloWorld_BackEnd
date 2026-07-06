# 게시판 댓글 기능 포맷
# 작성자 : 천석훈, 김세연, 문호성
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional

# 1. 공통 속성 스키마
class CommentBase(BaseModel):
    """
    댓글의 기본 속성을 정의하는 Base 스키마입니다.
    """
    content: str = Field(..., min_length=1, description="댓글 내용")

    @field_validator('content')
    @classmethod
    def validate_content_not_empty(cls, value: str) -> str:
        """
        요구사항 검증: 댓글에 내용이 없거나 공백(Space)만 포함된 경우를 차단합니다.
        """
        if not value.strip():
            raise ValueError('댓글 내용이 비어있거나 공백만 입력할 수 없습니다.')
        return value

# 2. 생성 요청 스키마
class CommentCreate(CommentBase):
    """
    클라이언트에서 댓글 생성을 요청할 때 사용하는 스키마입니다.
    - post_id: URL의 Path Parameter를 통해 전달받습니다.
    - user_id: 인증 토큰(JWT)에서 사용자 정보를 추출하여 매핑합니다.
    - 따라서 클라이언트의 Request Body에는 content만 포함됩니다.
    """
    pass

# 3. 응답 반환 스키마
class CommentResponse(CommentBase):
    """
    DB에 저장된 댓글 데이터를 클라이언트에게 반환할 때 사용하는 스키마입니다.
    """
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        # SQLAlchemy ORM 객체를 Pydantic 모델로 변환하기 위한 설정
        from_attributes = True 
        orm_mode = True # Pydantic V1 하위 호환