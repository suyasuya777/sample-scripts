"""
学習ポイント: 処理時間計測ミドルウェア（README main.pyの実装パターン）
- X-Process-Time ヘッダー: レスポンスに処理時間（秒）を付与
- time.time()            : リクエスト開始・終了時刻の計測
- パフォーマンス監視     : レスポンスヘッダーで処理時間を可視化
"""
import time
from fastapi import FastAPI, Request

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    README の main.py に実装されているミドルウェアと同じパターン。
    全リクエストの処理時間を X-Process-Time レスポンスヘッダーに付与する。
    """
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.middleware("http")
async def add_request_id_header(request: Request, call_next):
    """リクエストIDをヘッダーに付与（トレーサビリティ向上）"""
    import uuid
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response

@app.get("/items")
async def get_items():
    return [{"id": 1, "name": "PC"}]
