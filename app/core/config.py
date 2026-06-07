# 환경변수 (DB URL, JWT Secret 등)
# 작성자 : 엄인섭
import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 기본값(default)을 제거하여, .env 파일에 값이 없으면 에러가 발생하게 함
    DATABASE_URL: str 
    SECRET_KEY: str
    
    # Pydantic v2 방식의 설정
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()