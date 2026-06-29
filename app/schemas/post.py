# 작성자 : 엄인섭
# 게시글 작성 폼, 페이징 응답 폼
from pydantic import BaseModel, Field
from datetime import datetime

class PostPreviewResponse(BaseModel):
    id: int = Field(..., description="게시글 고유 번호 (상세 페이지 이동 시 사용)")
    title: str = Field(..., description="게시글 제목")
    category: str = Field(..., description="게시판 카테고리 (예: 공지, 일반, 질문)")
    author_role: str = Field(..., description="작성자 역할 (예: 회장, 부회장, 일반)")
    created_at: datetime = Field(..., description="게시글 생성(작성) 날짜 및 시간")

    class Config:
        from_attributes = True


class ClubFeedResponse(BaseModel):
    id: int = Field(..., description="게시글 고유 ID (클릭 시 해당 게시글로 이동)")
    title: str = Field(..., description="게시글 제목 (사진 캡션용)")
    image_url: str = Field(..., description="피드 썸네일 이미지 URL")
    created_at: datetime = Field(..., description="게시글 등록일")

    class Config:
        from_attributes = True