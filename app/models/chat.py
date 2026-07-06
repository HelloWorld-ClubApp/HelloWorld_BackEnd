# 채팅 관련 모델 (Chat_001~003, 파일 연동 및 읽음 상태 포함)
# 작성자 : 엄인섭
from datetime import datetime
from typing import List, Optional
from sqlalchemy import ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.user import User
from app.models.file import File

class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    messages: Mapped[List["Message"]] = relationship(back_populates="room", cascade="all, delete-orphan")
    participants: Mapped[List["ChatParticipant"]] = relationship(back_populates="room", cascade="all, delete-orphan")

class ChatParticipant(Base):
    __tablename__ = "chat_participants"
    
    room_id: Mapped[int] = mapped_column(ForeignKey("chat_rooms.id", ondelete="CASCADE"), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    room: Mapped["ChatRoom"] = relationship(back_populates="participants")
    user: Mapped["User"] = relationship("User")

class Message(Base):
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("chat_rooms.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    
    # 파일 모델 연결 (File 모델 존재 가정)
    file_id: Mapped[Optional[int]] = mapped_column(ForeignKey("files.id"), nullable=True) 
    
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    room: Mapped["ChatRoom"] = relationship(back_populates="messages")
    user: Mapped["User"] = relationship("User")
    
    # 파일 정보를 가져오기 위한 relationship
    file: Mapped[Optional["File"]] = relationship("File", foreign_keys=[file_id])
    
    # 읽음 상태 관리 (1:N)
    read_statuses: Mapped[List["MessageReadStatus"]] = relationship(back_populates="message", cascade="all, delete-orphan")

class MessageReadStatus(Base):
    """
    메시지별 읽음 상태 관리 테이블
    특정 메시지에 대해 누가 읽었는지 기록
    """
    __tablename__ = "message_read_statuses"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    
    message: Mapped["Message"] = relationship(back_populates="read_statuses")
    user: Mapped["User"] = relationship("User")