# 게시판 댓글 기능 포맷
# 작성자 : 천석훈, 김세연, 문호성
from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base # 동아리 기본 베이스 모델 임포트

class Comment(Base):
    __tablename__ = "comments" # 요구사항 DB 테이블명 일치

    # 1. id: INT SERIAL, PK (댓글 고유번호)
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # 2. user_id: INT NOT NULL, FK, CASCADE (사용자 고유번호 외래키)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # 3. post_id: INT NOT NULL, FK, CASCADE (게시글 고유번호 외래키)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    
    # 4. content: TEXT NOT NULL (댓글의 내용)
    content = Column(Text, nullable=False)
    
    # 5. created_at: TIMESTAMP NOT NULL, DEFAULT now() (댓글 생성 날짜 및 시간)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # 6. updated_at: TIMESTAMP DEFAULT CURRENT_TIMESTAMP (댓글 변경 시간)
    # onupdate=func.now()를 추가해서 수정될 때마다 자동으로 시간이 갱신되게 세팅!
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- 테이블 간의 관계(Relationship) 설정 ---
    # 나중에 댓글에서 작성자 정보나 게시글 정보를 쉽게 뽑아오기 위한 연결고리야!
    user = relationship("User", backref="comments")
    post = relationship("Post", backref="comments")