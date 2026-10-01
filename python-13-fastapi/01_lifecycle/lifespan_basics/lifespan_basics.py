"""
学習ポイント: lifespan で共有リソースを持つ
- lifespan          : yield の前が起動、後が終了。FastAPI 0.93+ の推奨パターン
- app.state         : 起動時に作ったリソースをリクエストから参照する置き場
- 起動時の疎通確認  : 外部依存に疎通をかけると、依存先の障害で自分が起動できなくなる
- 原則              : 「起動は通す、readiness で落とす」

SRE 的な論点:
  起動処理で外部APIやDBへ接続確認を行うと、依存先が落ちている間は
  ECS タスクが起動 → 失敗 → 再起動 のループに入り、ログだけが増える。
  起動は通してタスクを立ち上げ、readiness を 503 にして LB から外すほうが、
  依存先の復旧と同時に自動で復帰でき、調査もしやすい。
"""
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── startup ───────────────────────────────────────
    # 共有リソースはここで1つだけ作る（02_outbound/shared_client を参照）
    app.state.http = httpx.AsyncClient(
        timeout=httpx.Timeout(connect=3.0, read=5.0, write=5.0, pool=3.0),
        limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
    )
    # DB接続プールなども同様にここで生成する
    app.state.db = {"pool": "dummy-pool"}

    # 疎通確認はここでは行わない。readiness 側で継続的に判定する
    app.state.ready = True
    print("[startup] resources initialized")

    yield

    # ── shutdown ──────────────────────────────────────
    # 生成したものは必ず閉じる。閉じ忘れは接続リークになる
    await app.state.http.aclose()
    print("[shutdown] resources closed")


app = FastAPI(lifespan=lifespan)


@app.get("/whoami")
async def whoami(request: Request):
    """リクエストから共有リソースを参照する例"""
    client: httpx.AsyncClient = request.app.state.http
    return {"client_is_shared": client is request.app.state.http}
