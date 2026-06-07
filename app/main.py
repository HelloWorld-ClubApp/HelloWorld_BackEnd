# FastAPI 애플리케이션 진입점 (설정 로드, 라우터 등록)
from fastapi import FastAPI
from app.core.database import engine, Base
# 모든 모델을 임포트해야 Base.metadata가 테이블을 인식합니다.
from app.models.user import User, Role, Permission, RolePermission, EmailVerification
from app.models.post import Post, PostFile, PostReadLog, Like, Comment
from app.models.chat import ChatRoom, ChatParticipant, Message
from app.models.contest import Host, Category, Contest, ContestCategory
from app.models.schedule import Schedule, Idea
# FastAPI 앱 생성
app = FastAPI()


@app.on_event("startup")
def startup_event():
    # 로컬 DB 작업 시 테이블 자동 생성 (Alembic 도입 전까지 유용)
    Base.metadata.create_all(bind=engine)
    print("🚀 로컬 데이터베이스 테이블이 성공적으로 생성되었습니다.")