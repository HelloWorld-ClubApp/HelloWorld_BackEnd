from datetime import datetime
from pydantic import BaseModel, ConfigDict


class FeedCreate(BaseModel):
    title: str
    file_id: int


class FeedResponse(BaseModel):
    id: int
    title: str
    file_id: int
    file_url: str
    user_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
    
class FeedUpdate(BaseModel):
    file_id: int
    title: str    

class FeedDetailResponse(BaseModel):
    id: int
    title: str
    file_url: str
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
    
class FeedShareRequest(BaseModel):
    room_id: int
