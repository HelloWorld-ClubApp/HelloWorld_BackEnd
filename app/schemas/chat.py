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

# ==========================================
# [MY_002] 채팅방 이미지 및 파일 클라우드 응답 스키마
# 작성자 : 천석훈, 김세연, 문호성, 강기민
# ==========================================
class ChatCloudFileResponse(BaseModel):
    file_id: int = Field(..., description="파일 고유번호")
    file_url: str = Field(..., description="파일의 URL")
    file_type: str = Field(..., description="파일의 형식 (확장자)")
    file_size: int = Field(..., description="파일의 크기 (바이트 단위)")
    original_name: str = Field(..., description="파일의 원래 이름")
    created_at: datetime = Field(..., description="파일이 업로드된 날짜 및 시간")
    is_expired: bool = Field(..., description="30일 보관 기간 만료 여부 (True면 다운로드 제한)")
    
    class Config:
        from_attributes = True