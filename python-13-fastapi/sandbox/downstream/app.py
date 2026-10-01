"""下流ダミー API（教材 02_outbound / 07_integrated の検証用）

遅い・落ちる・429 を返す下流を、こちらの都合で作り出すためのサーバ。
起動: uvicorn downstream.app:app --host 0.0.0.0 --port 9001
"""
from __future__ import annotations

import asyncio
import random
import time

from fastapi import FastAPI, Header, Request
from fastapi.responses import JSONResponse, PlainTextResponse

app = FastAPI(title="downstream-stub")

# 障害注入のスイッチ（/control で切り替える）
STATE: dict[str, object] = {
    "outage": False,        # True の間は常に failure_status を返す
    "failure_status": 503,
    "fail_rate": 0.0,       # 0.0〜1.0 の確率で failure_status を返す
    "extra_delay": 0.0,     # すべての応答に加算する遅延（秒）
}


async def _delay() -> None:
    d = float(STATE["extra_delay"])  # type: ignore[arg-type]
    if d > 0:
        await asyncio.sleep(d)


def _maybe_fail() -> JSONResponse | None:
    if STATE["outage"]:
        return JSONResponse({"error": "outage"}, status_code=int(STATE["failure_status"]))  # type: ignore[arg-type]
    if random.random() < float(STATE["fail_rate"]):  # type: ignore[arg-type]
        return JSONResponse({"error": "flaky"}, status_code=int(STATE["failure_status"]))  # type: ignore[arg-type]
    return None


@app.get("/ok")
async def ok(x_request_id: str | None = Header(default=None)):
    """正常系。request_id の伝搬確認にも使う（受け取った値をそのまま返す）。"""
    await _delay()
    if (failed := _maybe_fail()) is not None:
        return failed
    return {"ok": True, "received_request_id": x_request_id, "ts": time.time()}


@app.get("/slow")
async def slow(seconds: float = 3.0):
    """read タイムアウトの検証用。応答開始まで seconds だけ待つ。"""
    await asyncio.sleep(seconds)
    return {"slept": seconds}


@app.get("/hang")
async def hang():
    """接続は張れるが応答が返らない。read タイムアウト未設定の怖さの再現用。"""
    await asyncio.sleep(3600)
    return {"never": True}


@app.get("/drip")
async def drip(chunks: int = 10, interval: float = 1.0):
    """少しずつ流し続ける。read タイムアウトが「無応答間隔」の上限である確認用。"""

    async def gen():
        for i in range(chunks):
            yield f"chunk {i}\n"
            await asyncio.sleep(interval)

    from fastapi.responses import StreamingResponse

    return StreamingResponse(gen(), media_type="text/plain")


@app.get("/status/{code}")
async def status_code(code: int):
    """任意のステータスを返す。4xx はリトライ対象外である確認に使う。"""
    await _delay()
    return JSONResponse({"code": code}, status_code=code)


@app.get("/throttle")
async def throttle(retry_after: int = 2):
    """429 + Retry-After。バックオフが Retry-After を優先するかの確認用。"""
    return JSONResponse(
        {"error": "too many requests"},
        status_code=429,
        headers={"Retry-After": str(retry_after)},
    )


@app.post("/echo")
async def echo(request: Request):
    """冪等キーの検証用。ボディと Idempotency-Key をそのまま返す。"""
    body = await request.body()
    await _delay()
    if (failed := _maybe_fail()) is not None:
        return failed
    return {
        "idempotency_key": request.headers.get("idempotency-key"),
        "body": body.decode() or None,
        "served_at": time.time(),
    }


@app.post("/control")
async def control(
    outage: bool | None = None,
    failure_status: int | None = None,
    fail_rate: float | None = None,
    extra_delay: float | None = None,
):
    """障害注入のスイッチ。例: curl -XPOST 'localhost:9001/control?outage=true'"""
    for key, value in {
        "outage": outage,
        "failure_status": failure_status,
        "fail_rate": fail_rate,
        "extra_delay": extra_delay,
    }.items():
        if value is not None:
            STATE[key] = value
    return STATE


@app.get("/healthz")
async def healthz():
    return PlainTextResponse("ok")
