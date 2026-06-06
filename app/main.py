# FastAPI 애플리케이션 진입점 (설정 로드, 라우터 등록)
from fastapi import FastAPI

# FastAPI 앱 생성
app = FastAPI(title="SNS App API", version="1.0.0")

# 서버가 잘 켜졌는지 확인하는 테스트 라우터
@app.get("/")
async def root():
    return {"message": "서버가 성공적으로 실행되었습니다! 🔥"}