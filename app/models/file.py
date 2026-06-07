# 파일 상세 메타데이터 관리 모델
# 작성자 : 엄인섭
from datetime import datetime
from sqlalchemy import String, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.core.database import Base

class File(Base):
    """
    [파일 테이블]
    JPG, PNG, PDF 등 모든 미디어 파일의 상세 메타데이터 관리
    """
    __tablename__ = "files"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False) # 파일의 URL
    file_type: Mapped[str] = mapped_column(String(50), nullable=False) # 파일의 형식 (JPG, PNG 등)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False) # 파일의 크기 (Byte)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False) # 파일의 이름
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())