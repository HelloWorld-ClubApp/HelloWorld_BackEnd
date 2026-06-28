# 게시판(공지, 자유, 질문), 좋아요 (Post_001~003)
# 작성자 : 엄인섭
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db # 또는 세션 의존성 주입 경로
from app.schemas.post import PostPreviewResponse
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


