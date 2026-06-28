# 작성자 : 엄인섭
# 링커리어 공모전 크롤링 스크립트 파일입니다. 실행 주기는 약 6개월에 한번씩 해주세요.
from dotenv import load_dotenv
load_dotenv()

import time
import requests
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.contest import Contest, Host, ContestCategory, Category

LINKAREER_GRAPHQL_URL = "https://api.linkareer.com/graphql"

CATEGORY_MAP = {
    "28": "기획/아이디어",
    "29": "광고/마케팅",
    "30": "사진/영상/UCC",
    "31": "디자인/순수미술/공예",
    "32": "네이밍/슬로건",
    "33": "캐릭터/만화/게임",
    "34": "건축/건설/인테리어",
    "35": "과학/공학",
    "36": "예체능/패션",
    "37": "전시/페스티벌",
    "38": "문학/시나리오",
    "39": "해외",
    "40": "학술",
    "41": "창업",
    "42": "기타"
}
def fetch_contests_from_api(session, category_id: str,page: int = 1):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    payload = {
        "operationName": "ActivityList_Activities",
        "variables": {
            "filterBy": {
                "status": "OPEN",
                "activityTypeID": "3",
                "categoryIDs": [category_id],
                "simpleApplyFilter": None
            },
            "pageSize": 20,
            "page": page,
            "activityOrder": {
                "field": "CREATED_AT",
                "direction": "DESC"
            }
        },
        "extensions": {
            "persistedQuery": {
                "version": 1,
                "sha256Hash": "44f302a1090cba62592f03df30951cb0ddde9db14008c0eebd933c4925fd8b97"
            }
        }
    }

    try:
        response = session.post(LINKAREER_GRAPHQL_URL, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json().get('data', {}).get('activities', {}).get('nodes', [])
    
    except Exception as e:
        print(f"[경고] {page}페이지 호출 중 문제 발생: {e}")
        return []
    

def get_or_create_host(db: Session, host_name: str) -> int:
    if not host_name: host_name = "미상"
    host = db.query(Host).filter(Host.host_name == host_name).first()
    if not host:
        host = Host(host_name=host_name)
        db.add(host)
        db.commit()
        db.refresh(host)
    return host.id

def get_or_create_category(db: Session, category_name: str) -> int:
    """카테고리 처리 함수 추가"""
    cat = db.query(Category).filter(Category.category_name == category_name).first()
    if not cat:
        cat = Category(category_name=category_name)
        db.add(cat)
        db.commit()
        db.refresh(cat)
    return cat.id

def save_contests_to_db(db: Session, contest_list: list, category_name: str):
    new_count = 0
    # 카테고리 이름으로 ID 조회 (없으면 생성)
    cat_id = get_or_create_category(db, category_name)
    today = date.today()
    
    for item in contest_list:
        # 고유 상세 링크
        detail_url = f"https://linkareer.com/activity/{item.get('id')}"
        
        # 1. 중복 확인
        contest = db.query(Contest).filter(Contest.detail_url == detail_url).first()
            
        if not contest:
            # 새로 생성
            recruit_close_at = item.get("recruitCloseAt")
            end_date = datetime.fromtimestamp(recruit_close_at / 1000.0).date() if recruit_close_at else None
            
            # 마감된 공모전은 패스
            if end_date and end_date < today:
                continue

            contest = Contest(
                title=item.get("title", "제목 없음"),
                poster_image_url=item.get("thumbnailImage", {}).get("url") if item.get("thumbnailImage") else None,
                detail_url=detail_url,
                host_id=get_or_create_host(db, item.get("organizationName")),
                end_date=end_date
            )
            db.add(contest)
            db.flush() # ID 생성
        
        # 2. 카테고리 연결 (이미 연결되어 있는지 확인 후 추가)
        link_exists = db.query(ContestCategory).filter(
            ContestCategory.contest_id == contest.id,
            ContestCategory.category_id == cat_id
        ).first()
        
        if not link_exists:
            link = ContestCategory(contest_id=contest.id, category_id=cat_id)
            db.add(link)
            new_count += 1
            
    db.commit()
    return new_count

def cleanup_old_contests(db: Session, months: int = 6):
    """
    지정된 개월 수보다 더 오래된(마감일 기준) 공모전을 삭제합니다.
    CASCADE 설정 덕분에 contest_categories 등 연관 데이터도 자동 삭제됩니다.
    """
    print(f"🧹 {months}개월 이상 지난 오래된 공모전을 정리합니다...")
    
    # 6개월 전 날짜 계산
    threshold_date = datetime.now() - timedelta(days=months * 30)
    
    # 마감일(end_date)이 6개월 전보다 이전인 공모전 찾기
    old_contests = db.query(Contest).filter(Contest.end_date < threshold_date.date()).all()
    
    count = 0
    for contest in old_contests:
        db.delete(contest)
        count += 1
    
    db.commit()
    print(f"✅ 총 {count}개의 오래된 공모전 데이터를 삭제했습니다.")

def run_crawler():
    db = SessionLocal()
    session = requests.Session()
    
    # 1. 오래된 데이터 정리 (실행할 때마다 6개월 지난 데이터는 정리)
    cleanup_old_contests(db, months=6)
    
    # 2. 우리가 설정한 IT 관련 타겟 카테고리 ID들
    TARGET_IDS = ["28", "35", "40", "41", "42"]
    
    print("🚀 선택된 IT 카테고리 전체 페이지 크롤링을 시작합니다...")
    
    for cat_id in TARGET_IDS:
        cat_name = CATEGORY_MAP.get(cat_id, "기타")
        print(f"\n📂 [{cat_name}] 분야 수집 시작...")
        
        page = 1
        while True:
            print(f" -> {cat_name} 분야 {page}페이지 수집 중...")
            contests = fetch_contests_from_api(session, cat_id, page=page)
            
            # 더 이상 가져올 데이터가 없으면 루프 탈출
            if not contests:
                print(f" -> {cat_name} 분야 데이터 수집 완료 (총 {page-1}페이지).")
                break
            
            # DB 저장
            saved = save_contests_to_db(db, contests, category_name=cat_name)
            print(f" -> {saved}개의 공모전 저장 완료.")
            
            # 다음 페이지로 이동
            page += 1
            
            # 🌟 매너 있는 크롤러: 3초 휴식 (너무 빨리 요청하면 차단될 수 있음)
            time.sleep(3)
        
    db.close()
    session.close()
    print("\n✅ 모든 카테고리의 크롤링 작업이 완료되었습니다!")
    

if __name__ == "__main__":
    run_crawler()