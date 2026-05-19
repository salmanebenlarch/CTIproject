from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_env: str = 'development'
    vt_api_key: str = 'replace_me'
    vt_base_url: str = 'https://www.virustotal.com/api/v3'
    cors_origins: str = 'http://localhost:5173'
    max_file_size_mb: int = 32
    request_timeout_seconds: int = 90
    poll_interval_seconds: int = 5
    poll_max_attempts: int = 15

    database_url: str = 'postgresql+psycopg://postgres:postgres@localhost:5432/secradar'
    jwt_secret_key: str = 'change-me-in-production-please-use-32-plus-chars'
    jwt_algorithm: str = 'HS256'
    access_token_expire_minutes: int = 12 * 60
    news_cache_ttl_seconds: int = 300
    news_image_cache_ttl_seconds: int = 1800
    hibp_api_key: str = ''
    hibp_user_agent: str = 'SecRadar/1.0'
    abuseipdb_api_key: str = ''  # ← nouveau

    demo_admin_username: str = 'admin'
    demo_admin_password: str = 'change-this-admin-password'
    demo_admin_display_name: str = 'SOC Admin'
    demo_user_username: str = 'analyst'
    demo_user_password: str = 'change-this-user-password'
    demo_user_display_name: str = 'Threat Analyst'

    @field_validator('vt_api_key', 'hibp_api_key', 'abuseipdb_api_key')  # ← ajouté ici
    @classmethod
    def validate_api_keys(cls, value: str) -> str:
        return value.strip()

    @field_validator('jwt_secret_key')
    @classmethod
    def validate_jwt_secret_key(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError('JWT_SECRET_KEY is required')
        if len(value) < 32:
            raise ValueError('JWT_SECRET_KEY must be at least 32 characters long')
        return value

    @field_validator('hibp_user_agent')
    @classmethod
    def validate_hibp_user_agent(cls, value: str) -> str:
        value = value.strip()
        return value or 'SecRadar/1.0'

    @property
    def cors_origins_list(self) -> List[str]:
        return [item.strip() for item in self.cors_origins.split(',') if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()