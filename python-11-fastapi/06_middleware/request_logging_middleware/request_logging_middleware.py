"""
学習ポイント: リクエストロギングミドルウェア
- @app.middleware("http") : 全リクエスト/レスポンスをインターセプト
- call_next(request)      : 次のミドルウェア/エンドポイントを呼び出す
- リクエスト情報の記録    : メソッド・パス・クライアントIP・処理時間
"""
import time
import logging
from fastapi import FastAPI, Request

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

@app.middleware("http")
async def request_logging_middleware(request: Request, call_next):
    start = time.time()
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"→ {request.method} {request.url.path} from {client_ip}")
    try:
        response = await call_next(request)
        duration = time.time() - start
        logger.info(f"← {response.status_code} {request.url.path} ({duration:.3f}s)")
        return response
    except Exception as e:
        logger.error(f"✗ {request.url.path} Error: {e}")
        raise

@app.get("/items")
async def get_items():
    return [{"id": 1, "name": "PC"}]
