# 작성자 : 엄인섭
# 게시글 작성 폼, 페이징 응답 폼
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime, datetime as dt

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

#===============================
# Post_001 공지사항 및 게시글 작성 폼 (유효성 검사 포함)
class PostCreate(BaseModel):
    """게시글 생성 시 프론트엔드로부터 전달받는 데이터 뼈대"""
    post_type: str = Field(..., description="게시글 타입 (예: 공지사항, 자유게시판)")
    title: str = Field(..., description="게시글 제목")
    content: str = Field(..., description="게시글 내용")
    image_url: Optional[str] = Field(None, description="첨부 이미지 URL (선택사항)")
    schedule_date: Optional[datetime] = Field(None, description="일정 선택 (선택 사항, 과거 날짜 불가)")

    @field_validator('post_type', 'title', 'content')
    @classmethod
    def check_not_empty(cls, value):
        """필수 항목 누락 방지 로직"""
        if not value or not value.strip():
            raise ValueError("필수 항목을 입력하세요")
        return value
    
    @field_validator('schedule_date')
    @classmethod
    def check_schedule_date(cls, value):
        """과거 날짜 입력 방지 로직"""
        if value is not None and value < dt.now():
            raise ValueError("현재시간보다 이전의 날짜는 선택할 수 없습니다")
        return value
    
# ===============================
# Post_L_002 자유게시판 전용
class FreePostResponse(BaseModel):
    """자유게시판 목록용 데이터 뼈대"""
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class FreePostListResponse(BaseModel):
    """자유게시판 목록 조회 최종 응답"""
    message: Optional[str] = None
    posts: List[FreePostResponse] = []

# ===============================
# Post_002 자유게시판 상세 및 수정/삭제 폼
class FreePostDetailResponse(BaseModel):
    """자유게시판 상세 조회 응답"""
    id: int
    title: str
    content: str
    image_url: Optional[str]
    created_at: datetime
    author_id: int # 본인 확인을 위해 필요

    class Config:
        from_attributes = True

class FreePostUpdate(BaseModel):
    """자유게시판 수정 폼"""
    title: str = Field(..., description="게시글 제목")
    content: str = Field(..., description="게시글 내용")
    image_url: Optional[str] = Field(None, description="첨부 이미지 URL")

    @field_validator('title', 'content')
    @classmethod
    def check_not_empty(cls, value):
        if not value or not value.strip():
            raise ValueError("필수 항목을 입력하세요")
        return value