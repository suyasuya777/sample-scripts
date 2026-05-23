"""
学習ポイント: レートリミット（APIアクセス頻度制限）
- slowapi         : FastAPI向けレートリミットライブラリ
- @limiter.limit() : エンドポイントごとに制限を設定
- Redisバックエンド: 分散環境での共有カウンター
- IPベース制限    : クライアントIPでリクエスト数をカウント
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# slowapi を使う場合（pip install slowapi）
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded

# ── シンプルなインメモリレートリミット実装例 ──────────────
import time
from collections import defaultdict
from fastapi import HTTPException

app = FastAPI()
request_counts: dict = defaultdict(list)
RATE_LIMIT = 5    # リクエスト数
WINDOW_SEC = 60   # 時間窓（秒）

def check_rate_limit(client_ip: str):
    now = time.time()
    window_start = now - WINDOW_SEC
    request_counts[client_ip] = [t for t in request_counts[client_ip] if t > window_start]
    if len(request_counts[client_ip]) >= RATE_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Limit: {RATE_LIMIT} per {WINDOW_SEC}s",
            headers={"Retry-After": str(WINDOW_SEC)},
        )
    request_counts[client_ip].append(now)

@app.get("/api/data")
async def get_data(request: Request):
    check_rate_limit(request.client.host)
    return {"data": "success", "remaining": RATE_LIMIT - len(request_counts[request.client.host])}
