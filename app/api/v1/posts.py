# 게시판(공지, 자유, 질문), 좋아요 (Post_001~003)
# 작성자 : 엄인섭
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from app.core.database import get_db # 또는 세션 의존성 주입 경로
from app.schemas.post import PostPreviewResponse, ClubFeedResponse, NoticeListResponse, PostCreate, FreePostListResponse,QuestionPostListResponse
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

#=============================
# Post_L_002 자유게시판 목록 조회 API
@router.get("/free", response_model=FreePostListResponse, summary="자유게시판 목록 조회")
def get_free_post_list(page: int = 1, db: Session = Depends(get_db)):
    """
    [Post_L_002] 자유게시판 게시글 목록 조회 API
    - 최신순으로 정렬된 10개의 게시글을 가져옵니다.
    - 게시글이 없으면 "등록된 게시글이 없습니다"라는 메시지와 함께 빈 리스트를 반환합니다.
    """
    # 1. CRUD 창고에서 자유게시판 데이터 가져오기
    posts_data = crud_post.get_free_posts(db=db, page=page, limit=10)
    
    # 2. 게시글이 없는 경우 친절한 안내 문구 설정
    if not posts_data:
        return {"message": "등록된 게시글이 없습니다.", "posts": []}
    
    # 3. 데이터 포장해서 배달!
    return {"posts": posts_data}

#=============================
# Post_002 자유게시판 작성/수정/삭제 API 추가
@router.post("/free", summary="자유게시판 게시글 작성")
def create_free_post_api(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    # 1. 작성 제한 확인 (5개)
    if crud_post.get_user_post_count(db, current_user.id, "자유게시판") >= 5:
        raise HTTPException(status_code=400, detail="자유게시판은 최대 5개까지만 작성 가능합니다.")
    
    # 2. 작성 로직 수행
    new_post = crud_post.create_post(db=db, post_data=post_in, user_id=current_user.id)
    return {"message": "게시글이 작성되었습니다.", "data": new_post}

@router.put("/free/{post_id}", summary="자유게시판 게시글 수정")
def update_free_post_api(
    post_id: int,
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    post = crud_post.get_post_by_id(db, post_id)
    if not post or post.category != "자유게시판":
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 권한 체크: 본인만 수정 가능
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인이 작성한 게시글만 수정 가능합니다.")
        
    updated_post = crud_post.update_free_post(db=db, post_id=post_id, post_data=post_in.dict())
    return {"message": "수정되었습니다.", "data": updated_post}

@router.delete("/free/{post_id}", summary="자유게시판 게시글 삭제")
def delete_free_post_api(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    post = crud_post.get_post_by_id(db, post_id)
    if not post or post.category != "자유게시판":
        raise HTTPException(status_code=404, detail="게시글을 찾을 수 없습니다.")
    
    # 권한 체크: 본인 또는 관리자(role_id=2 가정)만 삭제 가능
    # (실제 관리자 role 값에 맞춰 수정 필요)
    if post.user_id != current_user.id and current_user.role_id != 2:
        raise HTTPException(status_code=403, detail="삭제 권한이 없습니다.")
        
    crud_post.delete_free_post(db=db, post_id=post_id)
    return {"message": "삭제되었습니다."}


#=============================
# Post_L_003 질문게시판 목록 조회 API
@router.get("/question", response_model=QuestionPostListResponse, summary="질문게시판 목록 조회")
def get_question_post_list(page: int = 1, db: Session = Depends(get_db)):
    """
    [Post_L_003] 질문게시판 게시글 목록 조회 API
    - 최신순 정렬, 페이지당 10개 출력.
    - 게시글이 없을 경우 안내 문구 반환.
    """
    posts_data = crud_post.get_question_posts(db=db, page=page, limit=10)
    
    if not posts_data:
        return {"message": "등록된 게시글이 없습니다.", "posts": []}
    
    # 제목 말줄임표 처리 (백엔드 처리 요청 시 적용)
    for post in posts_data:
        if len(post.title) > 20:
            post.title = post.title[:20] + "..."
            
    return {"posts": posts_data}

# 질문게시판 작성, 수정, 삭제는 자유게시판 로직과 동일하게 진행 가능
# 필요 시 위와 같이 /question 경로로 CRUD API를 추가하여 사용


#=============================
# Post_003 질문게시판 작성/수정/삭제 API 추가
@router.post("/question", summary="질문게시판 게시글 작성")
def create_question_post_api(
    post_in: PostCreate,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """
    [Post_003] 질문게시판 작성
    - 5개 작성 제한 확인
    - 이미지/파일 확장자 및 용량 검증은 파일 업로드 공통 API(서비스)에서 처리됨
    """
    # 1. 작성 제한 확인 (5개)
    if crud_post.get_user_post_count(db, current_user.id, "질문") >= 5:
        raise HTTPException(status_code=400, detail="질문게시판은 최대 5개까지만 작성 가능합니다.")
    
    # 2. 작성 로직 수행 (프론트에서 post_in.post_type을 "질문"으로 보내야 함)
    new_post = crud_post.create_post(db=db, post_data=post_in, user_id=current_user.id)
    return {"message": "질문 게시글이 성공적으로 작성되었습니다.", "data": new_post}

@router.put("/question/{post_id}", summary="질문게시판 게시글 수정")
def update_question_post_api(
    post_id: int,
    post_in: PostCreate, 
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """[Post_003] 질문게시판 수정 (본인만 가능)"""
    post = crud_post.get_post_by_id(db, post_id)
    if not post or post.category != "질문":
        raise HTTPException(status_code=404, detail="해당 질문 게시글을 찾을 수 없습니다.")
    
    # 권한 체크: 본인만 수정 가능
    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="본인이 작성한 질문 게시글만 수정 가능합니다.")
        
    updated_post = crud_post.update_question_post(db=db, post_id=post_id, post_data=post_in.dict())
    return {"message": "질문 게시글이 수정되었습니다.", "data": updated_post}

@router.delete("/question/{post_id}", summary="질문게시판 게시글 삭제")
def delete_question_post_api(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """[Post_003] 질문게시판 삭제 (본인 또는 관리자만 가능)"""
    post = crud_post.get_post_by_id(db, post_id)
    if not post or post.category != "질문":
        raise HTTPException(status_code=404, detail="해당 질문 게시글을 찾을 수 없습니다.")
    
    # 권한 체크: 본인 또는 최고 관리자(role_id=2 가정)만 삭제 가능
    if post.user_id != current_user.id and getattr(current_user, 'role_id', None) != 2:
        raise HTTPException(status_code=403, detail="질문 게시글을 삭제할 권한이 없습니다.")
        
    crud_post.delete_question_post(db=db, post_id=post_id)
    return {"message": "질문 게시글이 성공적으로 삭제되었습니다."}