# 비밀번호를 검증하고 탈퇴 처리를 수행하는 핵심 로직
# 작성자 : 엄인섭
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.crud import crud_user
from app.models.user import User
from app.core.security import verify_password
from fastapi import UploadFile
from app.services import file_service
from app.core.enum.user import JoinStatus
from typing import Optional, List
import json
import datetime

def withdraw_user_account(db: Session, current_user: User, password_input: str):
    """
    [MY_007] 회원탈퇴 비즈니스 로직
    - 현재 비밀번호 일치 여부를 검증하고, 성공 시 Soft Delete를 수행합니다.
    """
    # 1. 입력받은 평문 비밀번호와 DB의 해시된 비밀번호 비교
    if not verify_password(password_input, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호가 일치하지 않습니다."
        )
    
    # 2. 비밀번호가 일치하면 Soft Delete 수행
    crud_user.soft_delete_user(db, current_user.id)
    
    return {"message": "회원탈퇴가 성공적으로 처리되었습니다."}

# ==========================================
# [MY_001] 프로필 수정 (이미지 검증 및 회원 상태 업데이트)
# 작성자 : 천석훈, 김세연, 문호성, 강기민
# ==========================================
def normalize_hashtags(hashtags: Optional[List[str]]) -> Optional[List[str]]:
    if hashtags is None:
        return None

    normalized = []
    for raw_hashtag in hashtags:
        value = raw_hashtag.strip()
        if not value:
            continue

        if value.startswith("[") and value.endswith("]"):
            try:
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                parsed_value = None

            if isinstance(parsed_value, list):
                normalized.extend(
                    str(item).strip()
                    for item in parsed_value
                    if str(item).strip()
                )
                continue

        if "," in value:
            normalized.extend(
                item.strip()
                for item in value.split(",")
                if item.strip()
            )
        else:
            normalized.append(value)

    return list(dict.fromkeys(normalized))


def update_profile_service(
    db: Session,
    current_user: User,
    status_in: Optional[str] = None,
    profile_image: Optional[UploadFile] = None,
    background_image: Optional[UploadFile] = None,
    bio: Optional[str] = None,
    hashtags: Optional[List[str]] = None,
):
    """
    프론트엔드에서 넘어온 상태값과 이미지를 처리합니다.
    1. 이미지가 있다면 file_service로 용량 / 확장자 검증을 보냅니다.
    2. 검증이 끝나면 crud_user를 통해 DB를 최신화합니다.
    3. 요구사항에 명시된 성공 메시지를 반환합니다.
    """
    file_id = None
    
    # 1. 프론트엔드에서 프로필 이미지를 같이 보낸 경우에만 검사 및 저장 실행
    if profile_image:
        # file_service가 용량, JPG/PNG 검사를 마치고 DB에 저장한 뒤 파일 고유 번호를 줌
        file_id = file_service.validate_and_upload_profile_image(db, profile_image)

    background_file_id = None
    if background_image:
        background_file_id = file_service.validate_and_upload_profile_image(db, background_image)
        
    # 2. DB 업데이트 부서(CRUD)에 지시
    updated_user = crud_user.update_user_profile(
        db=db,
        user_id=current_user.id,
        status_in=status_in,
        file_id=file_id,
        background_file_id=background_file_id,
        bio=bio,
        hashtags=normalize_hashtags(hashtags)
    )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다."
        )

    # 3. [요구사항 반영] 프론트엔드에 성공 메시지 반환
    return {
        "message": "변경이 완료되었습니다",
        "profile": crud_user.get_my_profile(db=db, user_id=current_user.id),
    }


def get_join_request_summary(db: Session):
    return {
        "pending_request_count": crud_user.count_pending_join_requests(db),
        "total_member_count": crud_user.count_approved_members(db),
    }


def get_join_request_count(db: Session):
    return {
        "pending_request_count": crud_user.count_pending_join_requests(db),
    }


def get_pending_join_requests(db: Session, skip: int = 0, limit: int = 50):
    users = crud_user.get_pending_join_requests(db, skip=skip, limit=limit)
    return [
        {
            "id": user.id,
            "name": user.name,
            "admission_year": user.admission_year,
            "requested_at": user.requested_at or user.created_at or datetime.datetime.now(datetime.timezone.utc),
        }
        for user in users
    ]


def approve_join_request(db: Session, user_id: int):
    user = crud_user.get_user_by_id(db, user_id)
    if not user or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가입 신청 사용자를 찾을 수 없습니다."
        )

    if user.join_status != JoinStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="대기 중인 가입 신청이 아닙니다."
        )

    approved_user = crud_user.approve_join_request(db, user)
    return {
        "id": approved_user.id,
        "name": approved_user.name,
        "join_status": approved_user.join_status,
        "message": "가입 신청을 승인했습니다.",
    }


def reject_join_request(db: Session, user_id: int):
    user = crud_user.get_user_by_id(db, user_id)
    if not user or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="가입 신청 사용자를 찾을 수 없습니다."
        )

    if user.join_status != JoinStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="대기 중인 가입 신청이 아닙니다."
        )

    rejected_user = crud_user.reject_join_request(db, user)
    return {
        "id": rejected_user.id,
        "name": rejected_user.name,
        "join_status": rejected_user.join_status,
        "message": "가입 신청을 거절했습니다.",
    }
