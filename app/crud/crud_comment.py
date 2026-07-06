# 게시판 댓글 기능 포맷
# 작성자 : 천석훈, 김세연, 문호성
from sqlalchemy.orm import Session
from app.models.post import Comment
from app.schemas.comment import CommentCreate

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
        return db.query(Comment).filter(Comment.post_id == post_id).order_by(Comment.created_at.asc()).all()

# 다른 파일(Service, Router)에서 쉽게 가져다 쓸 수 있도록 객체 생성
comment_crud = CRUDComment()