"""
学習ポイント: デプロイ時の 502 を消すシャットダウン順序
- 4段階: ① readiness を 503 に落とす ② 登録解除を待つ
         ③ 処理中リクエストの完了を待つ ④ リソースを閉じる
- 順序を守らないと、LB がまだ振っているのに受け口を閉じ、502 になる
- ①と②の間に必要な待ち時間 = ALB の登録解除遅延 + ヘルスチェックの検知時間

SRE 的な論点:
  「SIGTERM を受けたら即座に閉じる」実装が最も多い誤り。
  SIGTERM を受けた時点では、まだ ALB のターゲットグループに自分が登録されており、
  新規リクエストが飛んでくる。先に readiness を落として LB に外させ、
  外れるまで待ってから閉じる必要がある。

  待ち時間の計算例（ALB の場合）:
    ヘルスチェック間隔 10 秒 × 異常閾値 2 回 = 最大 20 秒で unhealthy 判定
    + 登録解除遅延（deregistration_delay）
    この合計より ECS の stopTimeout が短いと SIGKILL され、途中で切れる
"""
import asyncio
import signal
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# ── 調整値（環境に合わせる） ─────────────────────────
DRAIN_WAIT_SECONDS = 20.0      # LB が自分を外すまで待つ時間
INFLIGHT_WAIT_SECONDS = 30.0   # 処理中リクエストの完了を待つ上限

STATE = {"ready": True}
INFLIGHT = {"count": 0}


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # ── ① readiness を落とす ─────────────────────────
    STATE["ready"] = False
    print("[shutdown] 1/4 readiness -> 503")

    # ── ② LB が自分を外すのを待つ ────────────────────
    await asyncio.sleep(DRAIN_WAIT_SECONDS)
    print("[shutdown] 2/4 drain wait done")

    # ── ③ 処理中リクエストの完了を待つ ───────────────
    waited = 0.0
    while INFLIGHT["count"] > 0 and waited < INFLIGHT_WAIT_SECONDS:
        await asyncio.sleep(0.5)
        waited += 0.5
    print(f"[shutdown] 3/4 inflight={INFLIGHT['count']} waited={waited}s")

    # ── ④ リソースを閉じる ───────────────────────────
    print("[shutdown] 4/4 resources closed")


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def count_inflight(request: Request, call_next):
    """処理中リクエスト数を数える。ヘルスチェックは対象外"""
    if request.url.path in ("/livez", "/readyz"):
        return await call_next(request)
    INFLIGHT["count"] += 1
    try:
        return await call_next(request)
    finally:
        INFLIGHT["count"] -= 1


@app.get("/readyz")
async def readyz():
    if not STATE["ready"]:
        return JSONResponse(status_code=503, content={"status": "draining"})
    return {"status": "ready"}


@app.get("/slow")
async def slow():
    """シャットダウン中に処理が待たれることを確認するための遅いエンドポイント"""
    await asyncio.sleep(10)
    return {"done": True}


# ── uvicorn 側の設定も必要 ────────────────────────────
# uvicorn graceful_shutdown:app --timeout-graceful-shutdown 60
#   この値が ③ の待ち時間より短いと、処理中でも打ち切られる
#
# ── 動作確認 ──────────────────────────────────────────
# 1. 起動して /slow を叩く
# 2. 別ターミナルから kill -TERM <pid>
# 3. /slow が最後まで応答し、その後に closed が出ることを確認する
