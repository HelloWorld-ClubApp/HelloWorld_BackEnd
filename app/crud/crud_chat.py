# 채팅 내역 저장 쿼리 (참여자 검증 로직 추가)
# 작성자 : 엄인섭
from sqlalchemy.orm import Session
from app.models.chat import ChatRoom, ChatParticipant, Message, MessageReadStatus
from typing import List
from sqlalchemy import func


def get_existing_private_room(db: Session, user_ids: List[int]):
    # 참여자가 정확히 2명인 1:1 방인지 확인
    if len(user_ids) != 2:
        return None
    
    # 두 유저가 모두 참여하고 있는 방을 찾음
    # room_id별로 참여자 수가 2명인 방을 찾아서 필터링
    subquery = db.query(ChatParticipant.room_id).filter(
        ChatParticipant.user_id.in_(user_ids)
    ).group_by(ChatParticipant.room_id).having(func.count(ChatParticipant.user_id) == 2).subquery()
    
    return db.query(ChatRoom).filter(ChatRoom.id == subquery.c.room_id).first()


def create_chat_room(db: Session, title: str, user_ids: List[int]):
    # 1. 채팅방 생성
    room = ChatRoom(title=title)
    db.add(room)
    db.commit()
    db.refresh(room)
    
    # 2. 참여자 추가
    for user_id in user_ids:
        participant = ChatParticipant(room_id=room.id, user_id=user_id)
        db.add(participant)
    db.commit()
    return room

def get_user_rooms(db: Session, user_id: int):
    # 1. 사용자가 참여 중인 모든 채팅방 가져오기
    rooms = db.query(ChatRoom, ChatParticipant.is_pinned).join(
            ChatParticipant
        ).filter(
            ChatParticipant.user_id == user_id
        ).order_by(
            ChatParticipant.is_pinned.desc(), # 고정된 방 먼저
            ChatRoom.created_at.desc()         # 그 다음 최신순
        ).all()
    
    results = []
    for room in rooms:
        # 2. 마지막 메시지 가져오기 (room.messages와 relationship이 연결되어 있어 바로 조회 가능)
        last_msg = db.query(Message).filter(Message.room_id == room.id).order_by(Message.created_at.desc()).first()
        
        # 3. 해당 채팅방에서 '나'만 안 읽은 메시지 수 카운트
        # MessageReadStatus 모델과 Message를 조인하여 필터링
        unread_count = db.query(MessageReadStatus).join(Message).filter(
            Message.room_id == room.id,       # 이 방의 메시지 중
            MessageReadStatus.user_id == user_id, # 내가
            MessageReadStatus.is_read == False    # 안 읽은 것
        ).count()
        
        # 4. 데이터 가공 (스키마 정의와 일치시켜야 함)
        results.append({
            "id": room.id,
            "title": room.title,
            "last_message": last_msg.content if last_msg else "대화 내용이 없습니다.",
            "last_message_time": last_msg.created_at if last_msg else room.created_at,
            "unread_count": unread_count,
            "created_at": room.created_at
        })
    return results

# 참여자인지 확인하는 헬퍼 함수
def is_participant(db: Session, room_id: int, user_id: int) -> bool:
    return db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == user_id
    ).first() is not None

def add_message(db: Session, room_id: int, user_id: int, content: str, file_id: int = None):
    # 1. 메시지 저장
    msg = Message(room_id=room_id, user_id=user_id, content=content, file_id=file_id)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    
    # 2. 모든 참여자에게 읽음 상태 생성 (Bulk Insert)
    participants = db.query(ChatParticipant).filter(ChatParticipant.room_id == room_id).all()
    for p in participants:
        status = MessageReadStatus(
            message_id=msg.id, 
            user_id=p.user_id, 
            is_read=(p.user_id == user_id) # 보낸 사람은 읽음 처리
        )
        db.add(status)
    db.commit()
    return msg

def get_messages(db: Session, room_id: int, limit: int = 50, offset: int = 0):
    # 1. 최신 메시지부터 limit 개수만큼 조회 (desc)
    messages = db.query(Message)\
        .filter(Message.room_id == room_id)\
        .order_by(Message.created_at.desc())\
        .limit(limit)\
        .offset(offset)\
        .all()
    
    # 2. 내림차순(최신순)으로 가져왔으므로, 실제 UI에 뿌릴 때는 오름차순으로 뒤집어야 함
    messages.reverse()
    
    results = []
    for msg in messages:
        unread_count = db.query(MessageReadStatus).filter(
            MessageReadStatus.message_id == msg.id,
            MessageReadStatus.is_read == False
        ).count()
        
        msg_data = {
            "id": msg.id,
            "room_id": msg.room_id,
            "user_id": msg.user_id,
            "content": msg.content,
            "file_id": msg.file_id,
            "created_at": msg.created_at,
            "unread_count": unread_count
        }
        results.append(msg_data)
        
    return results

def mark_messages_as_read(db: Session, room_id: int, user_id: int):
    # 해당 방의 메시지 중 내 것이 아닌 것들을 읽음 처리
    from app.models.chat import MessageReadStatus
    db.query(MessageReadStatus).filter(
        MessageReadStatus.user_id == user_id,
        MessageReadStatus.is_read == False
    ).update({"is_read": True})
    db.commit()


def delete_message(db: Session, room_id: int, message_id: int, user_id: int):
    # 1. 삭제할 메시지 조회 (작성자 확인 포함 - 보안)
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.room_id == room_id,
        Message.user_id == user_id
    ).first()
    
    if not message:
        return None  # 메시지가 없거나 권한이 없음
    
    # 2. 메시지 삭제
    # MessageReadStatus는 ForeignKey에 ON DELETE CASCADE가 걸려있어 자동으로 삭제됨
    db.delete(message)
    db.commit()
    return message


def leave_chat_room(db: Session, room_id: int, user_id: int):
    # 1. 참여자 정보 조회 및 삭제
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == user_id
    ).first()
    
    if not participant:
        return False # 참여자가 아님
        
    db.delete(participant)
    
    # 2. 방에 남은 사람이 있는지 확인
    remaining_count = db.query(ChatParticipant).filter(ChatParticipant.room_id == room_id).count()
    
    # 3. 남은 사람이 0명이면 방 자체를 삭제 (Clean-up)
    if remaining_count == 0:
        room = db.query(ChatRoom).filter(ChatRoom.id == room_id).first()
        if room:
            db.delete(room)
            
    db.commit()
    return True


def toggle_chat_room_pin(db: Session, room_id: int, user_id: int):
    # 1. 특정 유저의 해당 방 참여 정보 조회
    participant = db.query(ChatParticipant).filter(
        ChatParticipant.room_id == room_id,
        ChatParticipant.user_id == user_id
    ).first()
    
    if not participant:
        return None # 참여자가 아님
        
    # 2. 상태 반전 (True -> False / False -> True)
    participant.is_pinned = not participant.is_pinned
    db.commit()
    db.refresh(participant) # 변경사항 반영 확인
    
    return participant