# 작성자 : 엄인섭
# 게시글 작성 폼, 페이징 응답 폼
from typing import List
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

#작성자 : 천석훈 , 김세연, 문호성
#=============================
# Post_L_001 공지사항 전용
class NoticeResponse(BaseModel):
    """공지사항 단건 조회 응답 뼈대"""
    id: int = Field(..., description="게시글 고유 번호 (상세 페이지 이동 시 사용 필수)")
    title: str = Field(..., description="게시글 제목 (프론트엔드에서 말줄임표 처리)")
    created_at: datetime = Field(..., description="게시글 생성 날짜 및 시간")

    class Config:
        from_attributes = True


class NoticeListResponse(BaseModel):
    """공지사항 목록 조회 최종 응답 패키지"""
    notices: List[NoticeResponse] = Field(..., description="최신순으로 정렬된 공지사항 리스트 (데이터가 없으면 빈 배열 [] 반환)")