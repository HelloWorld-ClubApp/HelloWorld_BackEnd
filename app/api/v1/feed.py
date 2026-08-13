from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.crud import crud_feed
from app.schemas.feed import FeedCreate, FeedResponse, FeedUpdate, FeedDetailResponse, FeedShareRequest
from app.api.dependencies import get_current_user
from app.models.user import User
from app.utils.ws_manager import manager
import json

router = APIRouter()


# ==========================================
# FEED_001
# 피드 등록
# ==========================================
@router.post(
    "",
    response_model=FeedResponse,
    status_code=status.HTTP_201_CREATED
)
def create_main_feed(
    feed_data: FeedCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_feed.create_feed(
        db=db,
        feed_data=feed_data,
        user_id=current_user.id
    )


# ==========================================
# FEED_002
# 피드 전체 조회
# ==========================================
@router.get(
    "",
    response_model=List[FeedResponse]
)
def read_feed_list(
    db: Session = Depends(get_db)
):
    return crud_feed.get_feed_list(db)


# ==========================================
# FEED_003
# 피드 삭제
# ==========================================
@router.delete(
    "/{feed_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def remove_feed(
    feed_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    feed = crud_feed.delete_feed(
        db=db,
        feed_id=feed_id
    )

    if not feed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="피드를 찾을 수 없습니다."
        )

    return None


@router.put(
    "/{feed_id}",
    response_model=FeedResponse
)
def update_main_feed(
    feed_id: int,
    feed_data: FeedUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    feed = crud_feed.update_feed(
        db=db,
        feed_id=feed_id,
        feed_data=feed_data
    )

    if not feed:
        raise HTTPException(
            status_code=404,
            detail="피드를 찾을 수 없습니다."
        )

    return feed


@router.get(
    "/{feed_id}",
    response_model=FeedDetailResponse
)
def get_feed_detail(
    feed_id: int,
    db: Session = Depends(get_db)
):
    feed = crud_feed.get_feed_detail(
        db=db,
        feed_id=feed_id
    )

    if not feed:
        raise HTTPException(
            status_code=404,
            detail="피드를 찾을 수 없습니다."
        )

    return feed

# ==========================================
# [FEED_006] 피드를 채팅방에 공유
# ==========================================
@router.post(
    "/{feed_id}/share",
    summary="피드를 채팅방에 공유"
)
async def share_feed(
    feed_id: int,
    data: FeedShareRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    message, error = crud_feed.share_feed_to_chat(
        db=db,
        feed_id=feed_id,
        room_id=data.room_id,
        user_id=current_user.id
    )

    # 피드 없음
    if error == "FEED_NOT_FOUND":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="피드를 찾을 수 없습니다."
        )

    # 채팅방 참여자가 아님
    if error == "NOT_PARTICIPANT":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="해당 채팅방의 참여자가 아닙니다."
        )
        
    # 메시지 생성 실패
    if message is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="피드 공유 메시지 생성에 실패했습니다."
        )

    # WebSocket 전송 데이터
    broadcast_data = {
        "type": "NEW_MESSAGE",
        "data": {
            "message_id": message.id,
            "user_id": current_user.id,
            "content": message.content,
            "file_id": message.file_id,
            "created_at": str(message.created_at)
        }
    }

    await manager.broadcast(
        json.dumps(
            broadcast_data,
            ensure_ascii=False
        ),
        data.room_id
    )

    return {
        "message": "피드가 채팅방에 공유되었습니다.",
        "message_id": message.id,
        "room_id": data.room_id,
        "file_id": message.file_id
    }