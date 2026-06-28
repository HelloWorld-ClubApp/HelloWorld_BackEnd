# 작성자 : 엄인섭
from pydantic import BaseModel, Field
from typing import Optional

# Home 상단 배너 응답 데이터
class BannerResponse(BaseModel):
    id: int = Field(..., description="공모전 고유번호")
    title: str = Field(..., description="공모전 제목")
    poster_image_url: Optional[str] = Field(None, description="포스터 이미지 URL")
    detail_url: str = Field(..., description="상세 페이지 이동 URL")

    class Config:
        from_attributes = True