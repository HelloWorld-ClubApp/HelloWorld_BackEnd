from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.crud import crud_chat

# 채팅방 개설 인원 제한(50명) 검사 로직


# ==========================================
# [MY_002] 채팅방 클라우드 파일 목록 가공 서비스
# 작성자 : 천석훈, 김세연, 문호성, 강기민
# ==========================================
def get_chat_cloud_files_service(db: Session, room_id: int):
    """
    특정 채팅방의 파일 목록을 조회하고, 30일 만료 여부를 계산하여 반환합니다.
    """
    # 1. 창고 직원(CRUD)에게 해당 채팅방의 파일 목록(최신순) 가져오라고 지시
    files = crud_chat.get_chat_room_files(db=db, room_id=room_id)
    
    # 2. 기준 시간(현재 시간) 가져오기
    now = datetime.now()
    
    # 3. 프론트엔드 전달용 데이터 가공 (is_expired 계산 로직)
    result = []
    for f in files:
        # 파일 등록일(created_at)에 30일을 더해서 '만료일'을 구함
        expiration_date = f.created_at + timedelta(days=30)
        
        # 현재 시간이 만료일을 지났으면 True, 아니면 False
        is_expired = now > expiration_date
        
        # 앞서 만든 ChatCloudFileResponse 스키마 양식에 맞게 딕셔너리로 조립
        file_data = {
            "file_id": f.id,
            "file_url": f.file_url,
            "file_type": f.file_type,
            "file_size": f.file_size, # 프론트엔드 기기 용량 부족 알림용 데이터!
            "original_name": f.original_name,
            "created_at": f.created_at,
            "is_expired": is_expired  # 30일 만료 여부 팩트 체크 완료!
        }
        result.append(file_data)
        
    return result