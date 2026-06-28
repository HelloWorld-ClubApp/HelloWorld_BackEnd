# SQLAlchemy 세션 생성 및 DB 연결 설정
# 작성자 : 엄인섭
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# 데이터베이스 연결 엔진 생성
engine = create_engine(settings.DATABASE_URL)

# DB 세션 생성 (나중에 DB 조작 시 사용)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 모든 모델이 상속받을 Base 클래스
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()