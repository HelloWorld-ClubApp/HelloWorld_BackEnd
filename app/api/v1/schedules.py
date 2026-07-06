# 캘린더, 일정 관리 (SCH_001~002)
# 작성자 : 엄인섭
from typing import List
from datetime import date
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

# 프로젝트 내부 모듈 import
from app.core.database import get_db
from app.api.dependencies import get_current_user  # 로그인 검증
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, CalendarEventResponse
from app.crud import crud_schedule
from app.models.user import User

router = APIRouter()

@router.get("", response_model=List[CalendarEventResponse], summary="월별 캘린더 일정 조회 (SCH_001)")
def get_calendar(
    year: int = Query(...), 
    month: int = Query(...), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # 💡 에러 수정: 유저 정보를 파라미터로 받아오도록 추가
):
    """
    [SCH_001] 동아리 일정(Post 공지)과 개인 일정(Schedule)을 통합하여 해당 월의 데이터를 조회합니다.
    """
    return crud_schedule.get_calendar_events(db, year, month, current_user.id)

@router.get("/daily", response_model=List[CalendarEventResponse], summary="일별 캘린더 리스트 조회 (SCH_002)")
def get_daily_schedules(
    target_date: date = Query(..., description="조회할 날짜 (YYYY-MM-DD 형식)"), 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    [SCH_002] 캘린더에서 특정 날짜를 클릭했을 때, 그날 하루의 [전체 일정]과 [개인 일정]을 리스트로 조회합니다.
    """
    return crud_schedule.get_daily_schedules(db, target_date, current_user.id)

@router.post("", status_code=status.HTTP_201_CREATED, summary="개인 일정 등록")
def register_schedule(
    data: ScheduleCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    return crud_schedule.create_user_schedule(db, data, current_user.id)

@router.put("/{id}", summary="개인 일정 수정")
def update_schedule(
    id: int, 
    data: ScheduleUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    updated_schedule = crud_schedule.update_schedule(db, id, current_user.id, data)
    if not updated_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일정을 찾을 수 없거나 수정 권한이 없습니다.")
    return {"message": "일정 수정 성공", "data": updated_schedule}

@router.delete("/{id}", summary="개인 일정 삭제")
def delete_schedule(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    success = crud_schedule.delete_schedule(db, id, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="일정을 찾을 수 없거나 삭제 권한이 없습니다.")
    return {"message": "일정 삭제 완료"}