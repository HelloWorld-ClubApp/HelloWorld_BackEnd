# 작성자 : 엄인섭
# 게시글 작성 폼, 페이징 응답 폼
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator, field_validator
from datetime import datetime, datetime as dt

class PostPreviewResponse(BaseModel):
    id: int = Field(..., description="게시글 고유 번호 (상세 페이지 이동 시 사용)")
    title: str = Field(..., description="게시글 제목")
    category: str = Field(..., description="게시판 카테고리 (예: 공지, 일반, 질문)")
    author_role: str = Field(..., description="작성자 역할 (예: 회장, 부회장, 일반)")
    created_at: datetime = Field(..., description="게시글 생성(작성) 날짜 및 시간")

"""
class ClubFeedResponse(BaseModel):
    id: int = Field(..., description="게시글 고유 ID (클릭 시 해당 게시글로 이동)")
    title: str = Field(..., description="게시글 제목 (사진 캡션용)")
    image_url: str = Field(..., description="피드 썸네일 이미지 URL")
    created_at: datetime = Field(..., description="게시글 등록일")

    class Config:
        from_attributes = True
"""

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
    notices: List[NoticeResponse] = Field(..., description="최신순으로 정렬된 공지 리스트 (데이터가 없으면 빈 배열 [] 반환)")

#===============================
# Post_001 공지사항 및 게시글 작성 폼 (유효성 검사 및 일정 모순 방지 포함) -> 수정자 : 엄인섭

class PostCreate(BaseModel):
    """
    [이슈 5, 6, 8 통합 반영] 게시글 생성 요청 DTO
    - 다중 파일 ID 배열(file_ids) 수신
    - 시작/종료 날짜의 논리적 모순 및 타임존 비교 정합성 보장
    """
    post_type: str = Field(..., description="게시글 타입 (예: 공지, 일반, 질문)")
    title: str = Field(..., description="게시글 제목")
    content: str = Field(..., description="게시글 내용")
    
    # [이슈 5번 해결] 단일 이미지 URL 대신 다중 파일 고유번호 목록 수신
    file_ids: List[int] = Field(default=[], description="첨부할 파일/사진 고유 ID 목록")
    
    # [이슈 8번 해결] 일정 시작일 및 마감일
    start_date: Optional[datetime] = Field(None, description="일정 시작 날짜 및 시간")
    end_date: Optional[datetime] = Field(None, description="일정 종료 날짜 및 시간")

    @field_validator('post_type', 'title', 'content')
    @classmethod
    def check_not_empty(cls, value):
        """필수 항목 누락 및 공백 입력 방지"""
        if not value or not value.strip():
            raise ValueError("필수 항목을 입력하세요.")
        return value

    @model_validator(mode='after')
    def validate_schedule_dates(self) -> 'PostCreate':
        """
        [이슈 8번 핵심 해결] 일정 날짜 모순 방지 및 타임존 비교 정합성 검증 로직
        - 1. 시작 날짜는 지정했는데 종료 날짜가 누락된 경우 -> 모순 에러
        - 2. 종료 날짜만 덜렁 들어온 경우 -> 모순 에러
        - 3. 종료 날짜가 시작 날짜보다 과거인 경우 -> 시간 역전 에러
        - 4. offset-naive / aware 비교 에러를 방지하기 위해 start_date의 tzinfo 반영
        """
        if self.start_date and not self.end_date:
            raise ValueError("일정의 시작 날짜가 있으면 종료 날짜도 반드시 입력해야 합니다.")
        
        if self.end_date and not self.start_date:
            raise ValueError("일정의 종료 날짜가 있으면 시작 날짜도 반드시 입력해야 합니다.")
            
        if self.start_date and self.end_date:
            # 타임존 일치화 (Offset-naive / aware 비교 에러 원천 차단)
            current_time = dt.now(self.start_date.tzinfo) if self.start_date.tzinfo else dt.now()
            
            if self.start_date < current_time:
                raise ValueError("시작 날짜는 현재 시간보다 이전일 수 없습니다.")
            if self.end_date < self.start_date:
                raise ValueError("종료 날짜는 시작 날짜보다 빠를 수 없습니다.")
                
        return self
    
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
    
    # ===============================
# Post_L_003 질문게시판 전용
class QuestionPostResponse(BaseModel):
    """질문게시판 목록용 데이터 뼈대"""
    id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionPostListResponse(BaseModel):
    """질문게시판 목록 조회 최종 응답"""
    message: Optional[str] = None
    posts: List[QuestionPostResponse] = []

class QuestionPostDetailResponse(BaseModel):
    """질문게시판 상세 조회 응답"""
    id: int
    title: str
    content: str
    image_url: Optional[str]
    created_at: datetime
    author_id: int

    class Config:
        from_attributes = True

        # ===============================
# Post_003 질문게시판 수정 폼
class QuestionPostUpdate(BaseModel):
    """질문게시판 수정 폼"""
    title: str = Field(..., description="게시글 제목")
    content: str = Field(..., description="게시글 내용")
    image_url: Optional[str] = Field(None, description="첨부 이미지 URL")

    @field_validator('title', 'content')
    @classmethod
    def check_not_empty(cls, value):
        if not value or not value.strip():
            raise ValueError("필수 항목을 입력하세요")
        return value
    

# ==========================================
# [MY_005, MY_006] 마이페이지 게시물 목록 응답 스키마
# 작성자 : 엄인섭
# ==========================================
# [리팩토링]: 게시글 목록/상세 응답 시 Aggregate(집계) 데이터와 좋아요 여부 포함
class PostListResponse(BaseModel):
    id: int = Field(..., description="게시글 고유번호")
    category: str = Field(..., description="게시판 카테고리")
    title: str = Field(..., description="게시글 제목")
    created_at: datetime = Field(..., description="게시글 작성 일시")
    like_count: int = Field(0, description="총 좋아요 수")
    comment_count: int = Field(0, description="총 댓글 수")
    is_liked: bool = Field(False, description="현재 로그인한 사용자의 좋아요 여부")

    class Config:
        from_attributes = True

class PaginatedPostResponse(BaseModel):
    total_count: int = Field(..., description="전체 게시글 수 (무한 스크롤 기준점)")
    posts: List[PostListResponse] = Field(..., description="게시글 목록 (최대 20개)")


# ==========================================
# [Post_D_001] 게시글 상세 조회용 응답 스키마
# 작성자: 엄인섭
# 목적: 게시글 본문, 좋아요 수, 댓글 목록을 한 번에 반환하기 위한 엄격한 타입 규격 정의
# ==========================================
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class CommentResponse(BaseModel):
    """댓글 단건을 담는 응답 뼈대"""
    id: int = Field(..., description="댓글 고유 번호")
    user_id: int = Field(..., description="작성자 고유 번호")
    content: str = Field(..., description="댓글 내용")
    created_at: datetime = Field(..., description="댓글 작성 시간")
    updated_at: datetime = Field(..., description="댓글 수정 시간")

    class Config:
        # [Pylance 최적화]: SQLAlchemy ORM 모델을 자동으로 Pydantic 딕셔너리로 읽을 수 있게 허용[cite: 10]
        from_attributes = True

class PostDetailInfo(BaseModel):
    """게시글 본문 상세 정보 뼈대"""
    id: int = Field(..., description="게시글 고유 번호")
    user_id: int = Field(..., description="작성자 고유 번호")
    category: str = Field(..., description="게시판 카테고리 (NOTICE, FREE, QUESTION 등)")
    title: str = Field(..., description="게시글 제목")
    content: str = Field(..., description="게시글 내용")
    schedule_date: Optional[datetime] = Field(None, description="일정 선택 날짜 (선택 사항)")
    created_at: datetime = Field(..., description="게시글 작성 시간")

    class Config:
        from_attributes = True

class PostDetailData(BaseModel):
    """게시글 상세 정보와 연관 데이터(좋아요, 댓글)를 하나로 묶는 데이터 영역"""
    post_info: PostDetailInfo = Field(..., description="게시글 본문 상세 정보")
    total_likes: int = Field(..., description="해당 게시글이 받은 총 좋아요 개수")
    comments: List[CommentResponse] = Field(default_factory=list, description="게시글에 달린 댓글 목록 (최신순)")

class PostDetailResponse(BaseModel):
    """프론트엔드로 최종 반환되는 게시글 상세 API 응답 뼈대"""
    data: PostDetailData = Field(..., description="조회된 상세 데이터")


# app/schemas/comment.py
class CommentUpdate(BaseModel):
    """[이슈 4] 댓글 수정을 위한 요청 데이터 스키마"""
    content: str = Field(..., description="수정할 댓글 내용")

    class Config:
        json_schema_extra = {"example": {"content": "수정된 댓글 내용입니다."}}