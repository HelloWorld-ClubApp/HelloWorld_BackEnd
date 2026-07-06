# 채팅 관리 API (Chat_001~003)
# 작성자 : 엄인섭
import json
from fastapi import APIRouter, Depends, status, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.schemas.chat import ChatRoomCreate, MessageCreate, ChatRoomResponse, MessageResponse
from app.crud import crud_chat
from app.models.user import User
from app.utils.ws_manager import manager
from app.core.database import SessionLocal

router = APIRouter()

# [Chat_001] 내 채팅 목록 조회
@router.get("/", response_model=List[ChatRoomResponse], summary="내 채팅방 목록 조회")
def get_my_chat_rooms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_chat.get_user_rooms(db, current_user.id)

@router.post("/", status_code=status.HTTP_201_CREATED, summary="채팅방 생성")
def create_room(
    data: ChatRoomCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.id not in data.user_ids:
        data.user_ids.append(current_user.id)
        
    # 1:1 채팅인 경우 기존 방 확인
    if len(data.user_ids) == 2:
        existing_room = crud_chat.get_existing_private_room(db, data.user_ids)
        if existing_room:
            return existing_room # 기존 방 반환

    return crud_chat.create_chat_room(db, data.title, data.user_ids)

# [Chat_003] 메시지 전송
@router.post("/{room_id}/messages", response_model=MessageResponse, summary="채팅 메시지 전송")
def send_message(
    room_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 해당 방의 참여자인지 확인하는 로직 추가 권장 (Security)
    return crud_chat.add_message(db, room_id, current_user.id, data.content, data.file_id)

# [Chat_003] 메시지 내역 조회
@router.get("/{room_id}/messages", response_model=List[MessageResponse], summary="채팅방 메시지 조회")
def get_messages(
    room_id: int,
    limit: int = 50,    # 추가
    offset: int = 0,    # 추가
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_chat.get_messages(db, room_id, limit, offset)


@router.websocket("/ws/{room_id}/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    room_id: int, 
    user_id: int
):
    await manager.connect(websocket, room_id)
    db = SessionLocal() 
    try:
        while True:
            # 1. JSON 문자열을 받음
            try:
                data_raw = await websocket.receive_text()
                data = json.loads(data_raw)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"type": "ERROR", "message": "잘못된 데이터 형식입니다."}))
                continue
            
            event_type = data.get("type") # "NEW_MESSAGE" 또는 "READ_UPDATE"

            # [상황 1] 새 메시지 전송
            if event_type == "NEW_MESSAGE":
                content = data["data"].get("content")
                file_id = data["data"].get("file_id") # 파일 ID 전달받음
                
                # DB 저장 (파일 첨부 포함)
                msg = crud_chat.add_message(db, room_id=room_id, user_id=user_id, content=content, file_id=file_id)
                
                if msg:
                    # 프론트엔드에게 보낼 응답 데이터 구성
                    response = {
                        "type": "NEW_MESSAGE",
                        "data": {
                            "message_id": msg.id,
                            "user_id": user_id,
                            "content": content,
                            "file_id": file_id,
                            "created_at": str(msg.created_at)
                        }
                    }
                    await manager.broadcast(json.dumps(response, ensure_ascii=False), room_id)
                else:
                    await websocket.send_text(json.dumps({"type": "ERROR", "message": "전송 실패"}))

            # [상황 2] 읽음 처리 요청
            elif event_type == "READ_UPDATE":
                # 해당 방의 내 메시지들 읽음 처리 (DB 업데이트)
                crud_chat.mark_messages_as_read(db, room_id, user_id)
                
                # 참여자들에게 "누가 이 방의 메시지를 읽었다"고 전파
                await manager.broadcast(json.dumps({"type": "READ_UPDATE", "user_id": user_id}), room_id)

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        await manager.broadcast(json.dumps({"type": "INFO", "message": f"User {user_id}님이 퇴장했습니다."}), room_id)
    finally:
        db.close()


@router.delete("/{room_id}/messages/{message_id}", summary="메시지 삭제")
def delete_message(
    room_id: int,
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 삭제 시도
    deleted_msg = crud_chat.delete_message(db, room_id, message_id, current_user.id)
    
    if not deleted_msg:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="메시지를 삭제할 권한이 없거나 찾을 수 없습니다."
        )
        
    # 2. 채팅방 참여자들에게 삭제 정보 전파
    broadcast_data = {
        "type": "DELETE_MESSAGE",
        "message_id": message_id
    }
    # WebSocket 매니저를 통해 브로드캐스트
    manager.broadcast(json.dumps(broadcast_data, ensure_ascii=False), room_id)
    
    return {"message": "메시지가 삭제되었습니다."}


@router.delete("/{room_id}/participants", summary="채팅방 나가기")
def leave_room(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1. 나가기 처리
    success = crud_chat.leave_chat_room(db, room_id, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="채팅방에 참여 중이 아니거나 방을 찾을 수 없습니다."
        )
    
    # 2. WebSocket 알림 (퇴장 전파)
    leave_msg = {
        "type": "INFO", 
        "message": f"{current_user.name}님이 나갔습니다."
    }
    # manager는 기존에 정의해둔 WebSocketManager 인스턴스
    manager.broadcast(json.dumps(leave_msg, ensure_ascii=False), room_id)    
    return {"message": "채팅방에서 나갔습니다."}



@router.patch("/{room_id}/pin", summary="채팅방 상단 고정/해제")
def toggle_pin(
    room_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # CRUD 함수 호출
    result = crud_chat.toggle_chat_room_pin(db, room_id, current_user.id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="채팅방 참여 정보를 찾을 수 없습니다."
        )
        
    return {"message": "고정 상태가 변경되었습니다.", "is_pinned": result.is_pinned}