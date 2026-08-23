# 댓글 작성 및 삭제, 조회 (Comment_001)
# 작성자 : 천석훈, 김세연, 문호성
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

# 동아리 프로젝트 구조에 맞춘 의존성 주입 (경로 확인 필수!)
from app.api.dependencies import get_db, get_current_user 
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.comment_service import CommentService
from app.models.user import User
from app.schemas.comment import CommentUpdate

comment_service = CommentService()

router = APIRouter(
    tags=["Comments"]
)

@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    post_id: int,
    comment_in: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    [Comment_001] 특정 게시글에 새로운 댓글을 작성합니다.
    - 권한: 로그인한 사용자 (JWT 인증)
    - 제약사항 1: 공지사항 게시글에는 댓글 작성 불가 (Service 단 검증)
    - 제약사항 2: 내용이 없거나 공백뿐인 댓글은 차단 (Schema 단 검증)
    """
    # 비즈니스 로직(Service)으로 모든 데이터를 넘겨서 처리를 위임합니다.
    return comment_service.create_comment(
        db=db, 
        post_id=post_id, 
        user_id=current_user.id, 
        comment_in=comment_in
    )


@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    [Comment_001] 특정 댓글을 삭제합니다.
    - 권한: 댓글 작성자 본인 (Service 단 검증)
    - 처리 방식: 데이터베이스에서 즉시 제거(Hard Delete)
    - 반환값: 프론트엔드 연동을 위한 성공 메시 반환
    """
    # 비즈니스 로직(Service)으로 삭제 처리를 위임합니다.
    return comment_service.delete_comment(
        db=db, 
        comment_id=comment_id, 
        user_id=current_user.id
    )


# ======================================================================
# 2. app/api/v1/comments.py (댓글 라우터)
# ======================================================================


# [이슈 4 해결] 댓글 수정 API 라우터 신설
@router.put("/{comment_id}", status_code=status.HTTP_200_OK, summary="댓글 수정")
def update_comment_api(
    comment_id: int,
    comment_in: CommentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    작성자 본인의 댓글 내용을 수정. (Service 계층으로 위임)
    """
    updated_comment = comment_service.update_comment(
        db=db, comment_id=comment_id, user_id=current_user.id, comment_in=comment_in
    )
    return {"message": "댓글이 성공적으로 수정되었습니다.", "data": updated_comment}

# [이슈 3 해결] 불필요한 단독 댓글 조회 API 사용 중지(Deprecated)[cite: 18]
@router.get("/post/{post_id}", deprecated=True, summary="[Deprecated] 댓글 단독 조회")
def get_comments(post_id: int, db: Session = Depends(get_db)):
    """
    게시글 상세 조회(/{post_id}/detail) API에 이미 댓글 목록 조인이 포함되어 있으므로,
    프론트엔드의 혼선을 막기 위해 해당 API는 Deprecated 처리
    """
    return comment_service.get_post_comments(db=db, post_id=post_id)

