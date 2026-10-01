"""
統合サンプル: 01〜06 で学んだものを1つのアプリにまとめたもの

起動:
    uvicorn app.main:app --port 8000 --timeout-graceful-shutdown 60

構成:
    lifecycle      起動・ヘルスチェック・graceful shutdown   (01)
    http_client    共有クライアント・タイムアウト・リトライ      (02)
    observability  リクエストID・アクセスログ・RED メトリクス   (03)
    errors         統一エラー形式・未捕捉例外                (04)

ミドルウェアの順序に注意:
    後から add したものが外側になる。リクエストIDは最も外側で採番したいので、
    observability.install を最後に呼ぶ。
"""
import asyncio
import logging

from fastapi import FastAPI, HTTPException, Request

from . import errors, lifecycle, observability
from .context import request_id_var
from .http_client import get_with_retry
from .logging_setup import setup_logging

setup_logging("INFO")
log = logging.getLogger("app")

app = FastAPI(title="SRE integrated sample", lifespan=lifecycle.lifespan)

errors.install(app)
lifecycle.install(app)        # inflight カウント（内側）
observability.install(app)    # リクエストID採番（外側）


@app.get("/")
async def root():
    return {"service": "integrated-sample", "request_id": request_id_var.get()}


@app.get("/slow")
async def slow(seconds: int = 5):
    """shutdown 中に待たれることを確認するためのエンドポイント"""
    await asyncio.sleep(seconds)
    return {"slept": seconds}


@app.get("/downstream/{post_id}")
async def downstream(post_id: int, request: Request):
    client = request.app.state.http
    r = await get_with_retry(
        client, f"https://jsonplaceholder.typicode.com/posts/{post_id}",
        request_id_var.get(),
    )
    return r.json()


@app.get("/boom")
async def boom():
    raise ValueError("this detail must not leak to the response")


@app.get("/notfound")
async def notfound():
    raise HTTPException(status_code=404, detail="order not found")
