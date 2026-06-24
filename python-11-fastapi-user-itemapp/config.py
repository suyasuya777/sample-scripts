from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str = "dev_secret"
    database_url: str = "sqlite+aiosqlite:///./.dev.db"
    model_config = SettingsConfigDict(env_file=".env")


@lru_cache
def get_settings():
    return Settings()
