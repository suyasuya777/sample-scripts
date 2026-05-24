"""
学習ポイント: async/await によるエンドポイント実装
- async def  : I/O待ち中に他のリクエストを処理できる非同期エンドポイント
- def        : CPU処理中心の同期エンドポイント（スレッドプールで実行）
- asyncio.sleep: I/O待ちのシミュレーション（実際はDB・HTTP・ファイルI/O）
"""
import asyncio
import time
from fastapi import FastAPI

app = FastAPI()

@app.get("/async")
async def async_endpoint():
    """非同期: 待機中に他リクエストを処理可能"""
    await asyncio.sleep(1)
    return {"type": "async", "message": "1秒の非同期待機完了"}

@app.get("/sync")
def sync_endpoint():
    """同期: スレッドプールで実行。待機中は他リクエストをブロックしない"""
    time.sleep(1)
    return {"type": "sync", "message": "1秒の同期待機完了"}

@app.get("/parallel")
async def parallel_tasks():
    """asyncio.gather で複数の非同期処理を並列実行"""
    async def task(name: str, delay: float):
        await asyncio.sleep(delay)
        return f"{name} completed"
    results = await asyncio.gather(
        task("Task A", 0.5),
        task("Task B", 0.3),
        task("Task C", 0.8),
    )
    return {"results": results}
