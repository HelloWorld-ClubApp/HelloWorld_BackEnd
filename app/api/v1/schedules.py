# 캘린더, 일정 관리 (SCH_001~002)
# 작성자 : 엄인섭
from typing import List
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session

# 프로젝트 내부 모듈 import
from app.core.database import get_db
from app.api.dependencies import get_current_user  # 로그인 검증
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, CalendarEventResponse
from app.crud import crud_schedule
from app.models.user import User

router = APIRouter()

@router.get("", response_model=List[CalendarEventResponse], summary="월별 캘린더 일정 조회")
def get_calendar(year: int = Query(...), month: int = Query(...), db: Session = Depends(get_db)):
    """
    동아리 일정(Schedule)과 공지사항(Post)을 통합하여 해당 월의 데이터를 조회합니다.
    """
    return crud_schedule.get_calendar_events(db, year, month)



@router.post("", status_code=status.HTTP_201_CREATED, summary="개인 일정 등록")
def register_schedule(
    data: ScheduleCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user) # 로그인한 유저 정보 가져오기
):
    # 로그인한 유저의 ID(current_user.id)를 작성자로 자동 할당
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
        # 일정이 없거나 본인 것이 아닐 때
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="일정을 찾을 수 없거나 수정 권한이 없습니다."
        )
        
    return {"message": "일정 수정 성공", "data": updated_schedule}


@router.delete("/{id}", summary="개인 일정 삭제")
def delete_schedule(
    id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # 삭제 로직 실행
    success = crud_schedule.delete_schedule(db, id, current_user.id)
    
    if not success:
        # 삭제 실패 시 (없거나 권한 없음)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="일정을 찾을 수 없거나 삭제 권한이 없습니다."
        )
        
    return {"message": "일정 삭제 완료"}