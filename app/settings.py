import os
from functools import lru_cache

from pydantic import field_validator
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
    MINIO_HOST_PRIVATE: str
    MINIO_HOST_PUBLIC: str
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    SECRET_KEY: str = ''
    ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 3600
    VERIFICATION_TOKEN_EXPIRE_MINUTES: int = 1440
    FRONTEND_URL: str = 'http://localhost:5173'
    SMTP_HOST: str = ''
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ''
    SMTP_PASSWORD: str = ''
    SMTP_FROM: str = ''
    SMTP_FROM_NAME: str = 'Psychology Reports'
    PORT: int = 8000
    DEBUG: bool = False
    CORS_ORIGINS: list[str] = [
        'http://localhost:8080',
        'https://localhost:8080',
        'http://localhost:5173',
        'https://localhost:5173',
        'http://127.0.0.1:5173',
        'https://127.0.0.1:5173',
    ]

    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        if not v:
            raise ValueError('SECRET_KEY must not be empty.')
        return v


@lru_cache
def get_settings() -> Settings:
    env = os.getenv('ENVIRONMENT', '')
    env_file = f'{env.lower()}.env'
    return Settings(_env_file=env_file)

settings = get_settings()