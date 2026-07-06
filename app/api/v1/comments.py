# 댓글 작성 및 삭제, 조회 (Comment_001)
# 작성자 : 천석훈, 김세연, 문호성
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List  # 👈 [추가됨] 댓글 '목록(여러 개)'을 반환하기 위해 필요해!

# 동아리 프로젝트 구조에 맞춘 의존성 주입 (경로 확인 필수!)
from app.api.dependencies import get_db, get_current_user 
from app.schemas.comment import CommentCreate, CommentResponse
from app.services.comment_service import comment_service
from app.models.user import User

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


@router.get("/post/{post_id}", response_model=List[CommentResponse], status_code=status.HTTP_200_OK)
def get_comments(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    [Comment_001] 특정 게시글에 달린 모든 댓글 목록을 조회합니다.
    - 권한: 누구나 볼 수 있음 (Depends(get_current_user) 없음)
    - 정렬: 작성 시간 기준 오름차순 (먼저 쓴 댓글이 위에 표시됨)
    """
    return comment_service.get_post_comments(db=db, post_id=post_id)