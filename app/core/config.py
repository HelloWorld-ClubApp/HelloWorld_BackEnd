# 환경변수 (DB URL, JWT Secret 등)
# 작성자 : 엄인섭
import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 기본값(default)을 제거하여, .env 파일에 값이 없으면 에러가 발생하게 함
    DATABASE_URL: str
    SECRET_KEY: str
    EMAIL_USER: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str

    SUPABASE_URL: Optional[str] = None
    SUPABASE_STORAGE_BUCKET: str = "uploads"
    SUPABASE_STORAGE_PUBLIC_BASE_URL: Optional[str] = None
    SUPABASE_S3_ENDPOINT: Optional[str] = None
    SUPABASE_S3_REGION: str = "ap-northeast-1"
    SUPABASE_S3_ACCESS_KEY_ID: Optional[str] = None
    SUPABASE_S3_SECRET_ACCESS_KEY: Optional[str] = None
    
    # Pydantic v2 방식의 설정
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")



settings = Settings()  # type: ignore[call-arg]
