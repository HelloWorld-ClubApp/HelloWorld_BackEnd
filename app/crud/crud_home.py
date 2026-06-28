# 작성자 : 엄인섭
from sqlalchemy.orm import Session
from app.models.contest import Contest
from datetime import date

# 홈페이지 상단 공모전 배너 조회 쿼리
def get_latest_it_banners(db: Session, limit: int = 5):
    # 1. IT 관련 키워드 리스트 (필요한 키워드를 마음껏 추가하세요!)
    keywords = ["IT", "SW", "소프트웨어", "해커톤", "데이터" , "데이터", "웹", "앱", "ICT", "개발", "코딩", "디지털","블록체인","보안"]
    
    # 2. 마감되지 않은 최신 공모전 50개를 먼저 가져옴(필터링을 위해 조금 넉넉히)
    all_contests = (
        db.query(Contest)
        .filter(Contest.end_date >= date.today())
        .order_by(Contest.created_at.desc())
        .limit(300) 
        .all()
    )
    
    # 3. 키워드가 포함된 공모전만 필터링 (Python 리스트 컴프리헨션 사용)
    filtered_contests = [
        c for c in all_contests 
        if any(keyword.lower() in c.title.lower() for keyword in keywords)
    ]
    
    # 4. 최종적으로 필요한 개수(limit)만큼만 반환
    return filtered_contests[:limit]