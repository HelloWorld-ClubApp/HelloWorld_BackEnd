from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# 👇 내 프로젝트 환경에 맞게 DB 세션과 유저 인증 함수 경로를 맞춰야 함! (기존 라우터 파일 참고)
from app.api.dependencies import get_db, get_current_user 
from app.crud import crud_idea
from app.schemas.idea import IdeaCreate, IdeaResponse

router = APIRouter()

@router.post("/", response_model=IdeaResponse)
def create_user_idea(
    idea: IdeaCreate, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """아이디어 노트 작성"""
    return crud_idea.create_idea(db=db, idea=idea, user_id=current_user.id)

@router.get("/", response_model=List[IdeaResponse])
def read_user_ideas(
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """아이디어 노트 목록 조회 (최신순)"""
    return crud_idea.get_ideas(db=db, user_id=current_user.id)

@router.delete("/{idea_id}")
def delete_user_idea(
    idea_id: int, 
    db: Session = Depends(get_db), 
    current_user = Depends(get_current_user)
):
    """아이디어 노트 삭제"""
    success = crud_idea.delete_idea(db=db, idea_id=idea_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="아이디어를 찾을 수 없거나 삭제할 권한이 없습니다.")
    return {"message": "아이디어가 성공적으로 삭제되었습니다."}