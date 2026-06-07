# FastAPI 애플리케이션 진입점 (설정 로드, 라우터 등록)
#작성자 : 엄인섭
from fastapi import FastAPI
from app.core.database import engine, Base
from contextlib import asynccontextmanager

# 모든 모델을 임포트해야 Base.metadata가 테이블을 인식합니다.

# 현재 비밀번호 찾기까지 필요한 model만 임포트했습니다. - 엄인섭
from app.models.file import File 
from app.models.user import User, Role, Permission, RolePermission, EmailVerification
#from app.models.post import Post, PostFile, PostReadLog, Like, Comment
#from app.models.chat import ChatRoom, ChatParticipant, Message
#from app.models.contest import Host, Category, Contest, ContestCategory
#from app.models.schedule import Schedule, Idea


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 켜질 때
    Base.metadata.create_all(bind=engine)
    print("🚀 DB 테이블 생성 완료")
    yield
    # 서버 꺼질 때 (필요시 DB 세션 종료 로직 등 추가)

    
app = FastAPI(lifespan=lifespan)