from functools import cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # .env の SECRET_KEY / DATABASE_URL に対応（環境変数名は大文字小文字を区別しない）
    secret_key: SecretStr
    database_url: str
    echo_sql: bool = False
    access_token_expire_minutes: int = 20
    cors_origins: list[str] = [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ]

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@cache
def get_settings() -> Settings:
    return Settings()
