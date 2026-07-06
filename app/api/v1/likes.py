# 작성자 : 엄인섭
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.api.dependencies import get_db, get_current_user 

from app.schemas.like import LikeToggleResponse
from app.crud import crud_like
from app.models.user import User

# 라우터 객체 초기화
router = APIRouter()

# ---------------------------------------------------------
# 엔드포인트: POST /api/v1/posts/{post_id}/likes
# 역할: 특정 게시글에 좋아요를 누르거나 취소합니다.
# ---------------------------------------------------------
@router.post("/{post_id}/likes", response_model=LikeToggleResponse)
def toggle_post_like(
    post_id: int,
    db: Session = Depends(get_db),                     
    current_user: User = Depends(get_current_user)       
):
    """
    게시글 좋아요 토글(추가/취소) API
    - 대상: 일반, 질문 게시판 (공지사항 불가)
    - 중복 호출 시 자동으로 상태가 토글 전환됩니다.
    """
    # CRUD 모듈의 비즈니스 로직 호출
    result = crud_like.toggle_like(db=db, post_id=post_id, user_id=current_user.id)
    
    # 상태에 따른 안내 메시지 분기 처리
    message = "좋아요가 추가되었습니다." if result["liked"] else "좋아요가 취소되었습니다."

    # Pydantic 응답 스키마에 맞춰 반환
    return LikeToggleResponse(
        message=message,
        liked=result["liked"],
        total_likes=result["total_likes"]
    )