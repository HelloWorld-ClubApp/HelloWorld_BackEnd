from pydantic import BaseModel
from datetime import datetime

# 1. 작성용 (프론트 -> 백)
class IdeaCreate(BaseModel):
    title: str
    content: str

# 2. 조회용 (백 -> 프론트)
class IdeaResponse(BaseModel):
    id: int
    title: str
    content: str
    updated_at: datetime

    class Config:
        from_attributes = True