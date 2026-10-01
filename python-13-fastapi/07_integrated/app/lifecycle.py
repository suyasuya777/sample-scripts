"""起動・ヘルスチェック・graceful shutdown（01_lifecycle）"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .http_client import build_client

log = logging.getLogger("app")

DRAIN_WAIT_SECONDS = 20.0
INFLIGHT_WAIT_SECONDS = 30.0

STATE = {"ready": False, "started": False}
INFLIGHT = {"count": 0}
HEALTH_PATHS = {"/livez", "/readyz", "/startupz", "/metrics"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── startup: 外部疎通は確認しない ────────────────
    app.state.http = build_client()
    STATE["started"] = True
    STATE["ready"] = True
    log.info("startup complete")

    yield

    # ── shutdown: 4段階 ──────────────────────────────
    STATE["ready"] = False
    log.info("shutdown 1/4 readiness -> 503")

    await asyncio.sleep(DRAIN_WAIT_SECONDS)
    log.info("shutdown 2/4 drain wait done")

    waited = 0.0
    while INFLIGHT["count"] > 0 and waited < INFLIGHT_WAIT_SECONDS:
        await asyncio.sleep(0.5)
        waited += 0.5
    log.info("shutdown 3/4 inflight drained",
             extra={"fields": {"remaining": INFLIGHT["count"], "waited_s": waited}})

    await app.state.http.aclose()
    log.info("shutdown 4/4 resources closed")


async def check_db() -> bool:
    return True


def install(app: FastAPI) -> None:
    @app.middleware("http")
    async def _count_inflight(request: Request, call_next):
        if request.url.path in HEALTH_PATHS:
            return await call_next(request)
        INFLIGHT["count"] += 1
        try:
            return await call_next(request)
        finally:
            INFLIGHT["count"] -= 1

    @app.get("/livez", tags=["health"])
    async def livez():
        return {"status": "alive"}

    @app.get("/startupz", tags=["health"])
    async def startupz():
        if not STATE["started"]:
            return JSONResponse(status_code=503, content={"status": "starting"})
        return {"status": "started"}

    @app.get("/readyz", tags=["health"])
    async def readyz():
        if not STATE["ready"]:
            return JSONResponse(status_code=503, content={"status": "draining"})
        if not await check_db():
            return JSONResponse(status_code=503, content={"status": "not ready", "db": "unavailable"})
        return {"status": "ready", "inflight": INFLIGHT["count"]}
