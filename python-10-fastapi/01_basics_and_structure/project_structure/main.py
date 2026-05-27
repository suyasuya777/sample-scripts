"""
学習ポイント: FastAPIプロジェクトの推奨フォルダ構成
- main.py        : エントリーポイント（ルーター登録・ミドルウェア設定）
- routers/       : エンドポイント定義（APIRouter）
- cruds/         : DB操作ロジック（ビジネスロジック層）
- schemas/       : Pydanticスキーマ（リクエスト・レスポンス定義）
- models/        : SQLAlchemy ORMモデル定義
- database.py    : DBエンジン・セッション管理
- config.py      : 環境変数・設定管理
- tests/         : pytestテスト群
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import Base, engine
from routers import item, user
import models  # noqa: F401 – ORMモデルをBaseに登録するためインポート


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="Sample Project Structure", lifespan=lifespan)

app.include_router(user.router)
app.include_router(item.router)