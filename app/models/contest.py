# 공모전 조회를 위한 테이블
# 작성자 : 엄인섭
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy import String, ForeignKey, DateTime, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.core.database import Base

class Host(Base):
    __tablename__ = "hosts"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    host_name: Mapped[str] = mapped_column(String(100), unique=True)

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    category_name: Mapped[str] = mapped_column(String(50), unique=True)

class Contest(Base):
    __tablename__ = "contests"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(512))
    poster_image_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    detail_url: Mapped[str] = mapped_column(String(512), unique=True)
    host_id: Mapped[int] = mapped_column(ForeignKey("hosts.id", ondelete="SET NULL"))
    reward_clss: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    categories: Mapped[List["ContestCategory"]] = relationship(back_populates="contest", cascade="all, delete-orphan")

class ContestCategory(Base):
    __tablename__ = "contest_categories"
    contest_id: Mapped[int] = mapped_column(ForeignKey("contests.id", ondelete="CASCADE"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    contest: Mapped["Contest"] = relationship(back_populates="categories")
    category: Mapped["Category"] = relationship()