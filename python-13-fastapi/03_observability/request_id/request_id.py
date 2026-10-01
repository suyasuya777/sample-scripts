"""
学習ポイント: 1リクエストを横断して追えるIDを持つ
- X-Amzn-Trace-Id : ALB が付与する。これを受け取って引き継ぐ
- ContextVar      : async でもリクエストごとに独立した値を持てる
- 下流への伝搬    : 外部呼び出しのヘッダに載せて初めて横断できる

SRE 的な論点:
  障害調査の第一歩は「問題のリクエストを1本特定する」こと。
  ALB のアクセスログには trace_id があるが、アプリログに同じIDがなければ
  突き合わせられない。時刻とパスだけで探すのは、秒間数百リクエストの
  環境では現実的ではない。
"""
import uuid
from contextvars import ContextVar

import httpx
from fastapi import FastAPI, Request

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

app = FastAPI()


def extract_or_new(request: Request) -> str:
    """ALB の trace id を優先し、なければ自分で採番する"""
    # 例: Root=1-63f1a2b3-1234567890abcdef12345678
    amzn = request.headers.get("x-amzn-trace-id")
    if amzn:
        for part in amzn.split(";"):
            if part.strip().startswith("Root="):
                return part.strip()[len("Root="):]
    # 自社プロキシが付けている場合
    if rid := request.headers.get("x-request-id"):
        return rid
    return uuid.uuid4().hex


@app.middleware("http")
async def assign_request_id(request: Request, call_next):
    rid = extract_or_new(request)
    token = request_id_var.set(rid)
    try:
        response = await call_next(request)
    finally:
        request_id_var.reset(token)
    # クライアントにも返す。問い合わせ時にこのIDを伝えてもらう
    response.headers["x-request-id"] = rid
    return response


@app.get("/downstream")
async def call_downstream(request: Request):
    """下流呼び出しにIDを載せる。ここを忘れると横断できない"""
    rid = request_id_var.get()
    headers = {"x-request-id": rid}
    async with httpx.AsyncClient(timeout=5.0) as client:  # 本来は共有クライアント
        r = await client.get("https://jsonplaceholder.typicode.com/posts/1", headers=headers)
    return {"request_id": rid, "status": r.status_code}


# ── 確認方法 ──────────────────────────────────────────
# curl -i localhost:8000/downstream            → x-request-id が返る
# curl -i -H 'x-request-id: mytest' localhost:8000/downstream  → mytest が引き継がれる
