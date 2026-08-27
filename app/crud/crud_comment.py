# 게시판 댓글 기능 포맷
# 작성자 : 천석훈, 김세연, 문호성
from sqlalchemy.orm import Session
from app.models.post import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate
from fastapi import HTTPException, status

class CRUDComment:
    def create_comment(self, db: Session, *, obj_in: CommentCreate, user_id: int, post_id: int) -> Comment:
        """
        [Comment_001] 새로운 댓글을 데이터베이스에 등록합니다.
        - 공지사항 여부 및 유효성 검증은 Service 레이어에서 선행됩니다.
        """
        db_obj = Comment(
            content=obj_in.content,
            user_id=user_id,
            post_id=post_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_comment(self, db: Session, comment_id: int) -> Comment:
        """
        댓글 고유 번호(ID)로 특정 댓글을 단건 조회합니다.
        - 삭제 시 본인 확인(권한 검증)을 위해 사용됩니다.
        """
        return db.query(Comment).filter(Comment.id == comment_id).first()

    def delete_comment(self, db: Session, *, comment_id: int) -> None:
        """
        [Comment_001] 요구사항 반영: 댓글을 데이터베이스에서 즉시 제거(Hard Delete)합니다.
        """
        obj = db.query(Comment).filter(Comment.id == comment_id).first()
        if obj:
            db.delete(obj)
            db.commit()

    def get_comments_by_post(self, db: Session, post_id: int):
        """
        특정 게시글(post_id)에 달린 모든 댓글을 작성 시간순(오름차순)으로 조회합니다.
        """
        rows = (
            db.query(Comment, User)
            .join(User, Comment.user_id == User.id)
            .filter(Comment.post_id == post_id)
            .order_by(Comment.created_at.asc())
            .all()
        )
        return [
            {
                "id": comment.id,
                "user_id": comment.user_id,
                "post_id": comment.post_id,
                "author_name": user.display_name,
                "content": comment.content,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
            }
            for comment, user in rows
        ]


    def update_comment(self, db: Session, comment_id: int, user_id: int, comment_in: CommentUpdate):
        """
        [이슈 4 해결] 댓글 수정 비즈니스 로직
        - 작성자 본인 여부를 엄격히 검증하고, 검증 통과 시 내용을 덮어씌움
        """
        # 1. 대상 댓글 존재 여부 확인
        comment = comment_crud.get_comment(db=db, comment_id=comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="해당 댓글을 찾을 수 없습니다."
            )

        # 2. 권한 검증: 요청자(user_id)와 댓글 작성자가 일치하는지 확인
        if comment.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="댓글을 수정할 권한이 없습니다."
            )

        # 3. 데이터 갱신 및 DB 커밋
        comment.content = comment_in.content
        db.commit()
        db.refresh(comment)
        
        return comment
# 다른 파일(Service, Router)에서 쉽게 가져다 쓸 수 있도록 객체 생성
comment_crud = CRUDComment()
