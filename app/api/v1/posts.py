# 게시판(공지, 자유, 질문), 좋아요 (Post_001~003)
# 작성자 : 엄인섭
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Any
from app.core.database import get_db # 또는 세션 의존성 주입 경로
from app.schemas.post import PostPreviewResponse, ClubFeedResponse, NoticeListResponse, PostCreate
from app.crud import crud_post
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/latest", response_model=List[PostPreviewResponse])
def get_latest_posts(db: Session = Depends(get_db)):
    posts_with_roles = crud_post.get_latest_posts(db)
    
    # 리스트 데이터 가공
    result = []
    for post, role_name in posts_with_roles:
        result.append({
            "id": post.id,
            "title": post.title,
            "category": post.category,
            "author_role": role_name, # 회장/부회장 정보
            "created_at": post.created_at
        })
    return result


@router.get("/feed", response_model=List[ClubFeedResponse], summary="메인 페이지 CLUB FEED (사진 앨범) 조회")
def get_club_feed(db: Session = Depends(get_db)):
    """
    첨부파일(사진)이 포함된 최신 게시글 4개를 조회합니다.
    - 게시글에 이미지가 여러 개일 경우 가장 첫 번째 이미지를 썸네일로 사용합니다.
    - 결과가 빈 배열([])일 경우 프론트엔드에서 예외 처리 화면을 보여줍니다.
    """
    return crud_post.get_club_feed(db=db, limit=4)
#작성자 : 천석훈 , 김세연, 문호성
#=============================
@router.get("/notices", response_model=NoticeListResponse, summary="공지사항 리스트 조회")
def get_notice_list_api(db: Session = Depends(get_db)):
    """
    [Post_L_001] 요구사항 정의서 연동 - 공지사항 게시판 목록 조회 API
    - DB에서 최신순으로 정렬된 10개의 공지사항 데이터를 호출합니다.
    - 만약 게시글이 없다면 빈 배열([])이 반환되며, 프론트엔드에서 "등록된 게시글이 없습니다"를 표시합니다.
    """
    # 1. 아까 2단계에서 만든 파이썬 엔진(crud_post)에게 DB에서 데이터 긁어오라고 명
    notices_data = crud_post.get_notice_list(db=db, limit=10)
    
    # 2. 1단계에서 만든 데이터 규격(NoticeListResponse)에 맞춰서 딕셔너리로 포장 후 배달!
    return {"notices": notices_data}

#=============================
# Post_001 공지사항 및 자유게시판 작성, 수정, 삭제 API
@router.post("/", summary="게시글 작성 (공지사항/자유게시판)")
def create_post_api(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user) # 현재 로그인한 사용자의 신분증(정보)
):
    """
    [Post_001] 게시글 작성 API
    - 스키마(PostCreate)를 통해 빈칸, 과거 날짜 여부는 이미 자동 필터링 되었습니다.
    - 공지사항일 경우, 직책이 [회장, 부회장, 총무]인지 최종 권한 검사를 수행합니다.
    """
    # 1. 권한 검사: 작성하려는 글이 '공지사항'일 때만 신분증 확인
    if post_in.post_type == "공지사항":
        allowed_roles = ["회장", "부회장", "총무"]
        # (주의: current_user.role 이름은 실제 User 모델 구조에 맞춰 변경해야 할 수 있음.)
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="공지사항을 작성할 권한이 없습니다."
            )
            
    # 2. 모든 검사를 통과했으니 CRUD 창고 지시서로 데이터 전달
    new_post = crud_post.create_post(db=db, post_data=post_in, user_id=current_user.id)
    return {"message": "게시글이 성공적으로 작성되었습니다.", "data": new_post}


@router.put("/{post_id}", summary="공지사항 게시글 수정")
def update_notice_api(
    post_id: int,
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """[Post_001] 게시글 수정 API"""
    if post_in.post_type == "공지사항":
        allowed_roles = ["회장", "부회장", "총무"]
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="공지사항을 수정할 권한이 없습니다."
            )
            
    updated_post = crud_post.update_notice_post(db=db, post_id=post_id, post_data=post_in)
    if not updated_post:
        raise HTTPException(status_code=404, detail="해당 게시글을 찾을 수 없습니다.")
    return {"message": "게시글이 성공적으로 수정되었습니다.", "data": updated_post}


@router.delete("/{post_id}", summary="공지사항 게시글 삭제")
def delete_notice_api(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """[Post_001] 게시글 삭제 API"""
    # 삭제 역시 최고 관리자 직책만 가능하도록 통제
    allowed_roles = ["회장", "부회장", "총무"]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="공지사항을 삭제할 권한이 없습니다."
        )
        
    deleted_post = crud_post.delete_notice_post(db=db, post_id=post_id)
    if not deleted_post:
        raise HTTPException(status_code=404, detail="해당 게시글을 찾을 수 없습니다.")
    return {"message": "게시글이 성공적으로 삭제되었습니다."}