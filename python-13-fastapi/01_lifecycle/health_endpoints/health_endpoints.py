"""
学習ポイント: liveness / readiness / startup を分ける
- /livez    : プロセスが生きているか。依存先は一切見ない
- /readyz   : リクエストを受け付けられるか。依存先の状態とシャットダウン状態を見る
- /startupz : 起動が完了したか。初期化が長いアプリで使う
- LB が叩くのは /readyz。オーケストレータが再起動判断に使うのは /livez

SRE 的な論点:
  readiness に DB 疎通を含めると、DB が落ちたときに全タスクが同時に
  unhealthy になり、LB から全台外れて 503 になる。DB が復旧しても
  ヘルスチェックの成功閾値ぶん復帰が遅れる。
  「この依存が死んだらサービスとして成立しないか」で含める/含めないを決める。
  読み取り専用の縮退運転ができるなら、含めないほうがよい。
"""
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()
START_TIME = time.monotonic()

# graceful shutdown 時にここを False にする（01_lifecycle/graceful_shutdown 参照）
STATE = {"ready": True, "started": False}


async def check_db() -> bool:
    """実際には SELECT 1 などを短いタイムアウトで投げる"""
    return True


@app.get("/livez", tags=["health"])
async def livez():
    """プロセス生存のみ。ここで依存先を見てはいけない"""
    return {"status": "alive", "uptime_seconds": int(time.monotonic() - START_TIME)}


@app.get("/startupz", tags=["health"])
async def startupz():
    if not STATE["started"]:
        return JSONResponse(status_code=503, content={"status": "starting"})
    return {"status": "started"}


@app.get("/readyz", tags=["health"])
async def readyz():
    """LB が叩くのはここ。shutdown 中は必ず 503 を返す"""
    if not STATE["ready"]:
        # ドレイニング中。LB に「もう振らないで」と伝える
        return JSONResponse(status_code=503, content={"status": "draining"})

    if not await check_db():
        return JSONResponse(
            status_code=503, content={"status": "not ready", "db": "unavailable"}
        )
    return {"status": "ready"}


@app.on_event("startup")
async def _mark_started():
    STATE["started"] = True
