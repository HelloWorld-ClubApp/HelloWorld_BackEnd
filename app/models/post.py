# Posts, Comments, Likes 등
# 작성자 : 엄인섭
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, ForeignKey, Text, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base

from app.models.user import User
from app.models.file import File

class Post(Base):
    __tablename__ = "posts"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    category: Mapped[str] = mapped_column(String(7))
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship()
    comments: Mapped[List["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    likes: Mapped[List["Like"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    post_files: Mapped[List["PostFile"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    read_logs: Mapped[List["PostReadLog"]] = relationship(back_populates="post", cascade="all, delete-orphan")

class PostFile(Base):
    __tablename__ = "post_files"
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id", ondelete="CASCADE"), primary_key=True)
    post: Mapped["Post"] = relationship(back_populates="post_files")
    file: Mapped["File"] = relationship()

class PostReadLog(Base):
    __tablename__ = "post_read_logs"
    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='unique_user_post_read_logs'),)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    post: Mapped["Post"] = relationship(back_populates="read_logs")

class Comment(Base):
    __tablename__ = "comments"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    post: Mapped["Post"] = relationship(back_populates="comments")

class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (UniqueConstraint('post_id', 'user_id', name='unique_user_post_like'),)
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    post: Mapped["Post"] = relationship(back_populates="likes")