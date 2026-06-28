# 작성자 : 엄인섭
# 홈 화면 데이터 조회 (Home_001~004)
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db # 또는 세션 의존성 주입 경로
from app.schemas.home import BannerResponse
from app.crud import crud_home

router = APIRouter()

# 홈페이지 상단 공모전 배너 조회
@router.get("/banners", response_model=List[BannerResponse])
def get_main_banners(db: Session = Depends(get_db)):
    banners = crud_home.get_latest_it_banners(db)
    return banners