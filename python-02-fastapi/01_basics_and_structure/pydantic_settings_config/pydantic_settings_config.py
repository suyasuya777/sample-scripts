"""
学習ポイント: pydantic-settings を使った環境変数管理
- BaseSettings  : .envファイルや環境変数を自動読み込み
- SettingsConfigDict: 設定クラスのメタ情報（読み込むファイル名等）
- lru_cache     : Settings()インスタンスをキャッシュして再生成コストを削減
- 環境別切り替え : APP_ENV変数でdevelopment/production/testingを切り替え
"""
import os
from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """全環境共通の設定"""
    app_name: str = "FastAPI Learning App"
    debug: bool = False
    secret_key: str = Field(min_length=8)
    database_url: str


class DevelopmentConfig(BaseConfig):
    debug: bool = True
    model_config = SettingsConfigDict(env_file=".env.development")


class ProductionConfig(BaseConfig):
    debug: bool = False
    model_config = SettingsConfigDict(env_file=".env.production")


class TestingConfig(BaseConfig):
    database_url: str = "sqlite:///:memory:"
    secret_key: str = "test-secret-key-for-testing"
    model_config = SettingsConfigDict(env_file=".env.test")


def get_config_class():
    env = os.getenv("APP_ENV", "development")
    return {"development": DevelopmentConfig,
            "production": ProductionConfig,
            "testing": TestingConfig}.get(env, DevelopmentConfig)


@lru_cache()
def get_settings():
    """
    @lru_cache() により初回呼び出し時のみインスタンスを生成。
    以降は同じオブジェクトを返すため、.envの読み込みは1度だけ。
    """
    return get_config_class()()


# FastAPIのDependsで使用する例
from fastapi import FastAPI, Depends
app = FastAPI()

@app.get("/config-info")
async def config_info(settings=Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "debug": settings.debug,
        "env": os.getenv("APP_ENV", "development"),
    }
