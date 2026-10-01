"""
学習ポイント: 全リクエストを漏れなく記録する
- try/finally : 例外で終わったリクエストもログに残す
- 除外        : ヘルスチェックを記録するとログ量とコストが跳ね上がる
- 記録項目    : method / path / status / duration_ms / client_ip / user_agent / bytes

SRE 的な論点:
  既存サンプルの多くは call_next の戻り値を使ってログを書くが、
  call_next が例外を投げると、その行に到達せずログが残らない。
  「500 が出ているのにアクセスログに該当リクエストがない」という
  最悪の調査状況を作るのがこのパターン。try/finally で必ず書く。

  クライアントIP は request.client.host ではなく X-Forwarded-For を見る。
  ALB 経由では前者は ALB の IP になる。ただし XFF はクライアントが偽装できるため、
  信頼できるプロキシが付けた最後の値を使う。
"""
import logging
import time

from fastapi import FastAPI, Request

log = logging.getLogger("access")
app = FastAPI()

EXCLUDE_PATHS = {"/livez", "/readyz", "/startupz", "/metrics"}


def client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        # ALB は右端に直近のホップを足す。信頼境界の1つ内側を採る
        return xff.split(",")[-1].strip()
    return request.client.host if request.client else "-"


@app.middleware("http")
async def access_log(request: Request, call_next):
    if request.url.path in EXCLUDE_PATHS:
        return await call_next(request)

    start = time.perf_counter()
    status = 500  # 例外時の既定値
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        log.info(
            "access",
            extra={"fields": {
                "method": request.method,
                "path": request.url.path,
                "status": status,
                "duration_ms": duration_ms,
                "client_ip": client_ip(request),
                "user_agent": request.headers.get("user-agent", "-"),
            }},
        )


@app.get("/ok")
async def ok():
    return {"ok": True}


@app.get("/boom")
async def boom():
    raise RuntimeError("intentional")   # これもログに残ることを確認する
