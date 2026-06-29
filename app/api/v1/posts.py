# 게시판(공지, 자유, 질문), 좋아요 (Post_001~003)
# 작성자 : 엄인섭
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db # 또는 세션 의존성 주입 경로
from app.schemas.post import PostPreviewResponse, ClubFeedResponse
from app.crud import crud_post

router = APIRouter()

@router.get("/latest", response_model=List[PostPreviewResponse])
def get_latest_posts(db: Session = Depends(get_db)):
    posts_with_roles = crud_post.get_latest_posts(db)
    
    # 리스트 데이터 가공
    result = []
    for post, role_name in posts_with_roles:
        result.append({
            "id": post.id,
            "title": post.title,
            "category": post.category,
            "author_role": role_name, # 회장/부회장 정보
            "created_at": post.created_at
        })
    return result


@router.get("/feed", response_model=List[ClubFeedResponse], summary="메인 페이지 CLUB FEED (사진 앨범) 조회")
def get_club_feed(db: Session = Depends(get_db)):
    """
    첨부파일(사진)이 포함된 최신 게시글 4개를 조회합니다.
    - 게시글에 이미지가 여러 개일 경우 가장 첫 번째 이미지를 썸네일로 사용합니다.
    - 결과가 빈 배열([])일 경우 프론트엔드에서 예외 처리 화면을 보여줍니다.
    """
    return crud_post.get_club_feed(db=db, limit=4)
