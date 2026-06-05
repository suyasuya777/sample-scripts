import asyncio
from db import engine, Base
import models.memo

# ==================================================
# DB作成＆テーブル作成
# ==================================================


# データベースの初期化
async def init_db():
    print("=== データベースの初期化を開始 ===")
    async with engine.begin() as conn:
        # 既存のテーブルを削除
        await conn.run_sync(Base.metadata.drop_all)
        # テーブルを作成
        await conn.run_sync(Base.metadata.create_all)


# スクリプトで実行時のみ実行
if __name__ == "__main__":
    asyncio.run(init_db())