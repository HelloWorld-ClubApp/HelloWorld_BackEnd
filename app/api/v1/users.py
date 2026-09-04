# 마이페이지, 프로필 수정, 회원탈퇴 (MY_001~007)
# 작성자: 엄인섭
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_join_manager, get_current_user # 토큰 검증 의존성
from app.models.user import User
from app.models.user import User
from app.models.file import File as FileModel
from app.schemas.post import PaginatedPostResponse
from app.schemas.user import (
    JoinRequestActionResponse,
    JoinRequestCountResponse,
    JoinRequestSummaryResponse,
    JoinRequestUserResponse,
    UserMeResponse,
    UserProfileUpdateResponse,
    UserProfileHeaderResponse,
    MemberGroupResponse,
    UserResponse,
    UserWithdrawRequest,
)
from typing import List
from app.crud import crud_post, crud_user
from app.services import user_service
from typing import Literal, Optional
from fastapi import UploadFile, File, Form
from app.core.enum.user import JoinStatus

router = APIRouter()


# ==========================================
# [MY_005] 내가 쓴 게시물 조회
# ==========================================
@router.get("/me/posts", response_model=PaginatedPostResponse, summary="내가 쓴 게시물 조회")
def get_my_posts_api(
    skip: int = Query(0, description="건너뛸 아이템 수 (offset)"),
    limit: int = Query(20, description="가져올 아이템 수 (최대 20개씩)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_count, posts = crud_post.get_posts_by_user(db, current_user.id, skip, limit)
    return {"total_count": total_count, "posts": posts}


# ==========================================
# [MY_006] 좋아요 누른 게시물 조회
# ==========================================
@router.get("/me/likes", response_model=PaginatedPostResponse, summary="좋아요 누른 게시물 조회")
def get_my_liked_posts_api(
    skip: int = Query(0, description="건너뛸 아이템 수 (offset)"),
    limit: int = Query(20, description="가져올 아이템 수 (최대 20개씩)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    total_count, posts = crud_post.get_liked_posts_by_user(db, current_user.id, skip, limit)
    return {"total_count": total_count, "posts": posts}



# ==========================================
# [MY_007] 기능 : 회원탈퇴 처리
# ==========================================
@router.delete("/me", summary="앱 탈퇴 처리 (비밀번호 검증 포함)")
def withdraw_user(
    request: UserWithdrawRequest,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    사용자 탈퇴 시 유의사항 동의 후, 현재 비밀번호를 입력받아 검증 후 Soft Delete 처리합니다.
    """
    return user_service.withdraw_user_account(db, current_user, request.current_password)


@router.get("/me", response_model=UserMeResponse, summary="내 프로필 상세 조회")
def get_my_profile_api(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = crud_user.get_my_profile(db=db, user_id=current_user.id)
    if not profile:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return profile


@router.get("/search", response_model=List[UserResponse], summary="사용자 검색")
def search_users(query: str, db: Session = Depends(get_db)):
    # 쿼리 결과인 User 객체들을 자동으로 UserResponse 모델로 변환하여 반환
    return db.query(User).filter(
        User.is_deleted == False,
        User.join_status == JoinStatus.APPROVED.value,
        (User.name.contains(query)) | (User.student_id.contains(query))
    ).all()


@router.get(
    "/join-requests/summary",
    response_model=JoinRequestSummaryResponse,
    summary="동아리 가입 신청 관리 요약 조회"
)
def get_join_request_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_join_manager)
):
    return user_service.get_join_request_summary(db)


@router.get(
    "/join-requests/count",
    response_model=JoinRequestCountResponse,
    summary="가입 승인 대기 수 조회"
)
def get_join_request_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_join_manager)
):
    return user_service.get_join_request_count(db)


@router.get(
    "/join-requests",
    response_model=List[JoinRequestUserResponse],
    summary="가입 신청 사용자 목록 조회"
)
def get_pending_join_requests(
    skip: int = Query(0, ge=0, description="건너뛸 가입 신청 수"),
    limit: int = Query(50, ge=1, le=100, description="가져올 가입 신청 수"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_join_manager)
):
    return user_service.get_pending_join_requests(db, skip=skip, limit=limit)


@router.post(
    "/join-requests/{user_id}/approve",
    response_model=JoinRequestActionResponse,
    summary="가입 신청 승인"
)
def approve_join_request(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_join_manager)
):
    return user_service.approve_join_request(db, user_id)


@router.post(
    "/join-requests/{user_id}/reject",
    response_model=JoinRequestActionResponse,
    summary="가입 신청 거절"
)
def reject_join_request(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_join_manager)
):
    return user_service.reject_join_request(db, user_id)


@router.get("/me/header", response_model=UserProfileHeaderResponse, summary="메인 헤더용 내 프로필 조회")
def get_my_header_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile_image_url = None
    
    # 1. 유저에게 등록된 프로필 사진 파일(file_id)이 있는지 확인
    if current_user.file_id:
        file_record = db.query(FileModel).filter(FileModel.id == current_user.file_id).first()
        if file_record:
            profile_image_url = crud_user.normalize_file_url(file_record.file_url)

    # 2. 결과 반환 (이미지가 없으면 profile_image_url은 None(null)으로 내려감)
    return {
        "name": current_user.name,
        "profile_image_url": profile_image_url
    }



@router.get("/members", response_model=List[MemberGroupResponse], summary="학년별 동아리 멤버 조회")
def get_club_members(
    see_all: bool = Query(False, description="True면 졸업생 포함 전체 조회"),
    db: Session = Depends(get_db)
):
    # 이제 리스트 안에 학년별로 묶인 객체들이 반환됩니다.
    return crud_user.get_club_members_grouped(db=db, see_all=see_all)

# ==========================================
# [MY_001] 프로필 수정 API (상태 및 이미지 변경)
# 작성자 : 천석훈, 김세연, 문호성, 강기민
# ==========================================
@router.put("/me/profile", response_model=UserProfileUpdateResponse, summary="[MY_001] 프로필 수정")
def update_my_profile(
    # JSON이 아니라 파일과 글자를 같이 보내야 해서(Form-Data), Form()을 씁니다!
    status: Optional[Literal["재학", "졸업", "취업"]] = Form(
        None,
        description="학적 상태 (재학, 졸업, 취업 중 택 1)"
    ),
    bio: Optional[str] = Form(
        None,
        max_length=255,
        description="상태 메시지"
    ),
    hashtags: Optional[List[str]] = Form(
        None,
        description="프로필 해시태그. FormData에서 hashtags 키를 반복해서 전송"
    ),
    profile_image: Optional[UploadFile] = File(
        None,
        description="변경할 프로필 이미지 (20MB 이하, jpg/png)"
    ),
    background_image: Optional[UploadFile] = File(
        None,
        description="변경할 프로필 배경 이미지 (20MB 이하, jpg/png)"
    ),
    db: Session = Depends(get_db), # DB 연결선 챙기기
    current_user = Depends(get_current_user) # 현재 접속 중인(로그인한) 사용자 확인
):
    """
    사용자의 학적 상태와 프로필 이미지를 수정합니다.
    - 규칙에 어긋나는 이미지 업로드 시 400 에러를 반환합니다.
    - 성공 시 {"message": "변경이 완료되었습니다"} 를 반환합니다.
    """
    # 1. 아까 만든 user_service에게 받은 재료 넘기기!
    result = user_service.update_profile_service(
        db=db,
        current_user=current_user,
        status_in=status,
        profile_image=profile_image,
        background_image=background_image,
        bio=bio,
        hashtags=hashtags,
    )
    
    # 2. 무사히 끝났으면 프론트엔드에게 성공 메시지 반환!
    return result
