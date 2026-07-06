# 마이페이지, 프로필 수정, 회원탈퇴 (MY_001~007)
# 작성자: 엄인섭
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.api.dependencies import get_current_user # 토큰 검증 의존성
from app.models.user import User
from app.models.file import File # DB 설계상의 files 테이블
from app.schemas.user import UserProfileHeaderResponse, MemberGroupResponse,UserResponse
from typing import List
from app.crud import crud_user

router = APIRouter()


@router.delete("/me", summary="앱 탈퇴 처리")
def withdraw_user(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # 1. 현재 세션(db)에서 다시 조회하여 세션과 연결 (Attached Object)
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="유저를 찾을 수 없습니다.")
        
    # 2. 상태 변경
    user.is_deleted = True
    
    # 3. 커밋
    db.commit()
    db.refresh(user) # 변경사항 반영 확인
    
    return {"message": "성공적으로 탈퇴 처리되었습니다."}


@router.get("/search", response_model=List[UserResponse], summary="사용자 검색")
def search_users(query: str, db: Session = Depends(get_db)):
    # 쿼리 결과인 User 객체들을 자동으로 UserResponse 모델로 변환하여 반환
    return db.query(User).filter(
        (User.name.contains(query)) | (User.student_id.contains(query))
    ).all()


@router.get("/me/header", response_model=UserProfileHeaderResponse, summary="메인 헤더용 내 프로필 조회")
def get_my_header_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile_image_url = None
    
    # 1. 유저에게 등록된 프로필 사진 파일(file_id)이 있는지 확인
    if current_user.file_id:
        file_record = db.query(File).filter(File.id == current_user.file_id).first()
        if file_record:
            profile_image_url = file_record.file_url

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