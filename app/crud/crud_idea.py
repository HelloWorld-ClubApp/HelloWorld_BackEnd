from sqlalchemy.orm import Session
from app.models.schedule import Idea  # 💡 뼈대는 기존 schedule.py에 있으니 거기서 가져옴!
from app.schemas.idea import IdeaCreate

# 1. 아이디어 작성
def create_idea(db: Session, idea: IdeaCreate, user_id: int):
    db_idea = Idea(
        user_id=user_id,
        title=idea.title,
        content=idea.content
    )
    db.add(db_idea)
    db.commit()
    db.refresh(db_idea)
    return db_idea

# 2. 아이디어 목록 조회 (최신순)
def get_ideas(db: Session, user_id: int):
    return db.query(Idea).filter(
        Idea.user_id == user_id
    ).order_by(
        Idea.updated_at.desc()
    ).all()

# 3. 아이디어 삭제
def delete_idea(db: Session, idea_id: int, user_id: int):
    db_idea = db.query(Idea).filter(
        Idea.id == idea_id, 
        Idea.user_id == user_id
    ).first()
    
    if db_idea:
        db.delete(db_idea)
        db.commit()
        return True
    return False