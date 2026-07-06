# 메시지 전송 및 채팅 관리 스키마
# 작성자 : 엄인섭
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import List,Optional

class ChatRoomCreate(BaseModel):
    user_ids: List[int] = Field(..., description="채팅에 참여할 사용자들의 고유번호 리스트")
    title: str = Field(..., description="채팅방의 제목")

class MessageCreate(BaseModel):
    content: str = Field(..., description="채팅 메시지 내용")
    file_id: Optional[int] = Field(None, description="첨부된 파일 ID (선택사항)")
    
class ChatRoomResponse(BaseModel):
    id: int = Field(..., description="채팅방 고유번호")
    title: str = Field(..., description="채팅방 제목")
    last_message: Optional[str] = Field(None, description="마지막 메시지 내용")      # 마지막 메시지 내용
    last_message_time: Optional[datetime] = Field(None, description="마지막 메시지 시간") # 마지막 메시지 시간
    unread_count: int =  Field(0, description="안 읽은 메시지 총합")                    # 안 읽은 메시지 총합
    created_at: datetime = Field(..., description="채팅방 만든일시")
    
    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: int = Field(..., description="메시지 고유번호")
    room_id: int = Field(..., description="메시지가 속한 채팅방 고유번호")
    user_id: int = Field(..., description="메시지 작성자 고유번호")
    content: str = Field(..., description="메시지 내용")
    file_id: Optional[int] = Field(None, description="첨부된 파일 ID")
    unread_count: int = Field(0, description="안 읽은 사람 수")
    created_at: datetime = Field(..., description="메시지 작성일시")
    
    class Config:
        from_attributes = True