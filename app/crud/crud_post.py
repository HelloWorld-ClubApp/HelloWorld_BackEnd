# 게시글 조회, 페이징 로직
# 작성자 : 엄인섭
from sqlalchemy.orm import Session
from sqlalchemy import case
from app.models.post import Post
from app.models.user import User , Role

def get_latest_posts(db: Session, limit: int = 3):
    return (
        db.query(Post, Role.role_name)
        .join(User, Post.user_id == User.id)
        .join(Role, User.role_id == Role.id)
        .order_by(
            case((Post.category == '공지', 0), else_=1), # 공지 우선순위
            Post.created_at.desc()                      # 최신순
        )
        .limit(limit)
        .all()
    )
