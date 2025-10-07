import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')
    DATABASE_TYPE: str
    DATABASE_HOST: str
    DATABASE_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    BROKER_URL: str
    REPORT_JAR_PATH: str
    REPORT_JAR_NAME: str
    REPORT_BASE_PATH: str
    MINIO_HOST: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    SECRET_KEY: str = ''
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3600
    PORT: int = 8000
    DEBUG: bool = False


@lru_cache
def get_settings() -> Settings:
    env = os.getenv('ENVIRONMENT', '')
    env_file = f'{env.lower()}.env'
    return Settings(_env_file=env_file)

settings = get_settings()