# 작성자 : 엄인섭
from sqlalchemy.orm import Session
from sqlalchemy import extract, cast, Date
from datetime import date
from app.models.schedule import Schedule
from app.models.post import Post # 공지사항 모델
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.core.enum.post import PostCategory

def get_calendar_events(
    db: Session,
    year: int,
    month: int,
    current_user_id: int
):
    """특정 연/월의 개인 일정 및 공지사항 일정을 통합 조회"""

    # 개인 일정
    schedules = (
        db.query(Schedule)
        .filter(Schedule.user_id == current_user_id)
        .filter(extract('year', Schedule.start_date) == year)
        .filter(extract('month', Schedule.start_date) == month)
        .all()
    )

    # 공지사항 중 일정이 선택된 데이터만 조회
    notices = (
        db.query(Post)
        .filter(Post.category == PostCategory.NOTICE.value)
        .filter(Post.start_date.isnot(None), Post.end_date.isnot(None))
        .filter(extract('year', Post.start_date) == year)
        .filter(extract('month', Post.start_date) == month)
        .all()
    )

    results = []

    # PERSONAL 매핑
    for s in schedules:
        results.append({
            "id": s.id,
            "title": s.title,
            "content": s.content,
            "start_date": s.start_date,
            "end_date": s.end_date,
            "category": "PERSONAL",
            "color": s.color,
            "author_id": s.user_id
        })

    # NOTICE 매핑
    for p in notices:
        results.append({
            "id": p.id,
            "title": p.title,
            "content": p.content,
            "start_date": p.start_date,
            "end_date": p.end_date,
            "category": "NOTICE",
            "color": "#FF0000",
            "author_id": p.user_id
        })

    return results

def get_daily_schedules(db: Session, target_date: date, current_user_id: int):
    """[SCH_002] 특정 일자의 전체/개인 일정 리스트를 통합 조회합니다."""
    # 1. 해당 일자의 개인 일정
    schedules = (
        db.query(Schedule)
        .filter(Schedule.user_id == current_user_id)
        .filter(cast(Schedule.start_date, Date) == target_date)
        .all()
    )
    
    # 2. 해당 일자의 전체 일정(공지사항)
    notices = (
        db.query(Post)
        .filter(Post.category == PostCategory.NOTICE.value)
        .filter(Post.start_date.isnot(None), Post.end_date.isnot(None))
        .filter(cast(Post.start_date, Date) <= target_date)
        .filter(cast(Post.end_date, Date) >= target_date)
        .all()
    )
    
    results = []
    for s in schedules:
        results.append({"id": s.id, "title": s.title, "content": s.content if s.content is not None else "", "start_date": s.start_date, "end_date": s.end_date, "category": "PERSONAL", "color": s.color, "author_id": s.user_id})
    for p in notices:
        results.append({"id": p.id, "title": p.title, "content": p.content if p.content is not None else "", "start_date": p.start_date, "end_date": p.end_date, "category": "NOTICE", "color": "#FF0000", "author_id": p.user_id})
        
    return results

def create_user_schedule(db: Session, schedule_data: ScheduleCreate, user_id: int):
    db_schedule = Schedule(
        user_id=user_id,
        title=schedule_data.title,
        content=schedule_data.content,
        start_date=schedule_data.start_date,
        end_date=schedule_data.end_date,
        color=schedule_data.color
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def update_schedule(db: Session, sid: int, user_id: int, data: ScheduleUpdate):
    schedule = db.query(Schedule).filter(Schedule.id == sid, Schedule.user_id == user_id).first()
    if not schedule:
        return None 
    schedule.title = data.title
    schedule.content = data.content
    schedule.start_date = data.start_date
    schedule.end_date = data.end_date
    schedule.color = data.color
    db.commit()
    db.refresh(schedule)
    return schedule

def delete_schedule(db: Session, sid: int, user_id: int):
    schedule = db.query(Schedule).filter(Schedule.id == sid, Schedule.user_id == user_id).first()
    if not schedule:
        return False 
    db.delete(schedule)
    db.commit()
    return True
