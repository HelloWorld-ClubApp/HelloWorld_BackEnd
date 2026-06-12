# FastAPI 애플리케이션 진입점 (설정 로드, 라우터 등록)
# 작성자 : 엄인섭
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.database import engine, Base, SessionLocal

# ==========================================
# 1. 모델 임포트 (DB 테이블 생성용)
# 참조되는 테이블(부모)이 먼저 임포트 되어야 합니다.
# ==========================================
from app.models.file import File 
from app.models.user import User, Role, Permission, RolePermission, EmailVerification
from app.models.chat import ChatRoom, Message # (ChatParticipant는 chat.py 안에 있다고 가정)
from app.models.contest import Host, Category, Contest, ContestCategory
from app.models.post import Post, PostFile, PostReadLog, Like, Comment
from app.models.schedule import Schedule, Idea

# ==========================================
# 라우터(API) 임포트
# ==========================================
from app.api.v1 import auth

def init_seed_data():
    """서버 시작 시 필수 기초 데이터(Seed Data)를 DB에 넣는 함수"""
    db = SessionLocal()
    try:
        # 우리가 정의한 동아리 필수 역할 목록
        required_roles = ["일반회원", "회장", "부회장", "총무"]
        
        added_new_role = False
        for role_name in required_roles:
            # 해당 이름의 권한이 DB에 없으면 추가
            existing_role = db.query(Role).filter(Role.role_name == role_name).first()
            if not existing_role:
                db.add(Role(role_name=role_name))
                added_new_role = True
                
        if added_new_role:
            db.commit()
            print("🌱 기초 데이터(권한: 일반회원, 회장, 부회장, 총무)가 성공적으로 동기화되었습니다.")
        else:
            print("✅ 기초 데이터(권한)가 이미 완벽하게 세팅되어 있습니다.")
            
    except Exception as e:
        print(f"기초 데이터 생성 중 오류 발생: {e}")
    finally:
        db.close()

# ==========================================
# Lifespan 설정 (서버 시작/종료 이벤트)
# ==========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 서버 켜질 때
    Base.metadata.create_all(bind=engine)
    init_seed_data()
    print("🚀 로컬 데이터베이스 테이블이 성공적으로 생성되었습니다.")
    yield
    # 서버 꺼질 때 로직 추가 가능

# ==========================================
# FastAPI 앱 생성
# ==========================================
app = FastAPI(lifespan=lifespan)

# ==========================================
# 라우터 등록 (반드시 app 생성 이후에 위치해야 함!)
# ==========================================
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])