import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# ==================================================
# DBアクセス
# ==================================================
# ベースクラスの定義
Base = declarative_base()

# DBファイル作成
base_dir = os.path.dirname(__file__)
# データベースのURL
DATABASE_URL = "sqlite+aiosqlite:///" + os.path.join(base_dir, "memodb.sqlite")

# 非同期エンジンの作成
engine = create_async_engine(DATABASE_URL, echo=True)

# 非同期セッションの設定
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


# DBとのセッションを非同期的に扱うことができる関数
async def get_dbsession():
    async with async_session() as session:
        yield session
