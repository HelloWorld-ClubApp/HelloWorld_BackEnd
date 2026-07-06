# 작성자 : 엄인섭
from pydantic import BaseModel, Field
from datetime import datetime

class CalendarEventResponse(BaseModel):
    id: int = Field(..., description="일정 고유번호 (PK)")
    title: str = Field(..., description="일정의 제목")
    start_date: datetime = Field(..., description="일정 시작 시간 (ISO 포맷)")
    end_date: datetime = Field(..., description="일정 종료 시간 (ISO 포맷)")
    category: str = Field(..., description="일정 유형: 'NOTICE'(전체 공지), 'PERSONAL'(개인 일정)")
    color: str = Field(..., description="일정 마커 색상 (Hex 코드)") # SCH_001 색상 표시 요구사항 반영
    author_id: int = Field(..., description="작성자 유저 고유번호")
    
    class Config:
        from_attributes = True

class ScheduleBase(BaseModel):
    title: str = Field(..., description="일정 제목")
    start_date: datetime = Field(..., description="시작 일시")
    end_date: datetime = Field(..., description="종료 일시")
    color: str = Field("#3B82F6", description="일정 마커 색상 (Hex 코드)")

class ScheduleCreate(ScheduleBase):
    pass

class ScheduleUpdate(ScheduleBase):
    pass