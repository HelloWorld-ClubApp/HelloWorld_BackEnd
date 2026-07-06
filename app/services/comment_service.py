# 게시판 댓글 기능 포맷
# 작성자 : 천석훈, 김세연, 문호성
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.crud.crud_comment import comment_crud
from app.crud.crud_post import post_crud 
from app.schemas.comment import CommentCreate
from app.models.post import Comment

class CommentService:
    def create_comment(self, db: Session, post_id: int, user_id: int, comment_in: CommentCreate) -> Comment:
        """
        [Comment_001] 댓글 생성 비즈니스 로직
        - 게시글의 존재 여부 및 '공지사항' 여부를 검증합니다.
        """
        # 1. 대상 게시글 존재 여부 확인
        post = post_crud.get_post(db=db, post_id=post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 게시글을 찾을 수 없습니다."
            )
        
        # 2. post.py에 정의된 'category' 변수명 완벽 적용
        if post.category == "NOTICE": 
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="공지사항 게시글에는 댓글을 작성할 수 없습니다."
            )

        # 3. 검증 완료 시 CRUD를 통해 DB 저장
        return comment_crud.create_comment(db=db, obj_in=comment_in, user_id=user_id, post_id=post_id)

    def delete_comment(self, db: Session, comment_id: int, user_id: int) -> dict:
        """
        [Comment_001] 댓글 삭제 비즈니스 로직
        - 삭제 권한(본인 여부)을 검증하고, DB에서 즉시 제거(Hard Delete)합니다.
        """
        # 1. 대상 댓글 존재 여부 확인
        comment = comment_crud.get_comment(db=db, comment_id=comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 댓글을 찾을 수 없습니다."
            )

        # 2. [권한 검증]: 요청자와 댓글 작성자 일치 여부 확인
        if comment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="댓글을 삭제할 권한이 없습니다."
            )

        # 3. 즉시 제거 (Hard Delete) 로직 실행
        comment_crud.delete_comment(db=db, comment_id=comment_id)
        
        # 4. 프론트엔드 처리를 위한 메시지 반환
        return {"message": "삭제된 댓글입니다."}
    
    def get_post_comments(self, db: Session, post_id: int):
        """
        [Comment_001] 특정 게시글의 댓글 목록 조회
        - 게시글 존재 여부를 먼저 확인한 후, 댓글 리스트를 반환합니다.
        """
        # 1. 대상 게시글이 존재하는지 먼저 확인! (없으면 404 에러)
        post = post_crud.get_post(db=db, post_id=post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="해당 게시글을 찾을 수 없습니다."
            )
            
        # 2. 안전하게 해당 게시글의 댓글 목록 쓸어오기!
        return comment_crud.get_comments_by_post(db=db, post_id=post_id)

comment_service = CommentService()