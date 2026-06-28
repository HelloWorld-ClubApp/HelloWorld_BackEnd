# 작성자 : 엄인섭
from sqlalchemy.orm import Session
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from sqlalchemy.orm import Session
from sqlalchemy import extract
from app.models.schedule import Schedule
from app.models.post import Post # 공지사항 모델
from app.models.user import User

def get_calendar_events(db: Session, year: int, month: int, current_user_id: int):
    # 1. 개인 일정 (Schedule)
    schedules = (
        db.query(Schedule)
        .filter(Schedule.user_id == current_user_id) # ★ 핵심: 내 일정만!
        .filter(extract('year', Schedule.start_date) == year)
        .filter(extract('month', Schedule.start_date) == month)
        .all()
    )
    
    # 2. 공지사항 (Post)
    notices = (
        db.query(Post)
        .filter(Post.category == '공지') # 공지사항 전체
        .filter(extract('year', Post.created_at) == year)
        .filter(extract('month', Post.created_at) == month)
        .all()
    )
    
    results = []
    
    # 개인 일정 매핑
    for s in schedules:
        results.append({
            "id": s.sid,
            "title": s.title,
            "start_date": s.start_date,
            "end_date": s.end_date,
            "category": "PERSONAL", 
            "color": s.color, # DB에 저장된 유저의 선택 색상
            "author_id": s.user_id
        })
        
    # 공지사항 매핑
    for p in notices:
        results.append({
            "id": p.id,
            "title": p.title,
            "start_date": p.created_at,
            "end_date": p.created_at,
            "category": "NOTICE",
            "color": "#FF0000", # 공지사항은 백엔드에서 고정값 할당
            "author_id": p.user_id
        })
        
    return results


def create_user_schedule(db: Session, schedule_data: ScheduleCreate, user_id: int):
    # Pydantic 모델의 데이터를 딕셔너리로 변환하여 DB 모델 생성
    db_schedule = Schedule(
        user_id=user_id,
        title=schedule_data.title,
        start_date=schedule_data.start_date,
        end_date=schedule_data.end_date,
        color=schedule_data.color
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule



def update_schedule(db: Session, sid: int, user_id: int, data: ScheduleUpdate):
    # 1. sid와 user_id가 일치하는 일정만 조회 (본인 인증)
    schedule = db.query(Schedule).filter(Schedule.id == sid, Schedule.user_id == user_id).first()
    
    if not schedule:
        return None # 일정을 못 찾았거나, 내 일정이 아님
    
    # 2. 값 업데이트
    schedule.title = data.title
    schedule.start_date = data.start_date
    schedule.end_date = data.end_date
    schedule.color = data.color
    
    db.commit()
    db.refresh(schedule)
    return schedule



def delete_schedule(db: Session, sid: int, user_id: int):
    # 본인 소유의 일정인지 확인 후 조회
    schedule = db.query(Schedule).filter(Schedule.id == sid, Schedule.user_id == user_id).first()
    
    if not schedule:
        return False # 일정이 없거나 본인 소유가 아님
    
    db.delete(schedule)
    db.commit()
    return True