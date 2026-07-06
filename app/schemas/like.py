# 작업자 : 엄인섭
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

# ---------------------------------------------------------
# Like 토글 응답 스키마 (좋아요 누르기/취소하기 공통 응답)
# 역할: API 호출 시 프론트엔드에 반환될 데이터의 구조를 정의합니다.
# 프론트엔드 작업자의 이해를 돕기 위해 Field를 사용하여 설명과 예시를 추가했습니다.
# ---------------------------------------------------------
class LikeToggleResponse(BaseModel):
    message: str = Field(
        ..., 
        description="처리 결과 메시지 (상태에 따라 '좋아요가 추가되었습니다.' 또는 '좋아요가 취소되었습니다.' 반환)",
        example="좋아요가 추가되었습니다."
    )
    liked: bool = Field(
        ..., 
        description="현재 로그인한 사용자의 최종 좋아요 상태 (True: 좋아요 눌림, False: 좋아요 취소됨)",
        example=True
    )
    total_likes: int = Field(
        ..., 
        description="해당 게시글의 실시간 총 좋아요 누적 개수",
        example=42
    )

# ---------------------------------------------------------
# Like 기본 응답 스키마 (필요 시 목록 조회 등에 사용)
# 역할: DB의 likes 테이블 레코드를 직렬화하여 반환할 때 사용합니다.
# ---------------------------------------------------------
class LikeResponse(BaseModel):
    id: int = Field(
        ..., 
        description="좋아요 고유번호 (PK)", 
        example=1
    )
    post_id: int = Field(
        ..., 
        description="좋아요가 눌린 게시글의 고유번호 (FK)", 
        example=15
    )
    user_id: int = Field(
        ..., 
        description="좋아요를 누른 사용자의 고유번호 (FK)", 
        example=5
    )
    created_at: datetime = Field(
        ..., 
        description="좋아요를 누른 날짜 및 시간"
    )

    model_config = ConfigDict(from_attributes=True)