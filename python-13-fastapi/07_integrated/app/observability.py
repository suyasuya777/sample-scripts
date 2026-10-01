"""リクエストID・アクセスログ・RED メトリクス（03_observability）"""
import logging
import time
import uuid

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

from .context import request_id_var

log = logging.getLogger("access")

EXCLUDE = {"/livez", "/readyz", "/startupz", "/metrics"}

REQUESTS = Counter("http_requests_total", "リクエスト総数", ["method", "path", "status"])
LATENCY = Histogram(
    "http_request_duration_seconds", "処理時間", ["method", "path"],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)


def _request_id(request: Request) -> str:
    amzn = request.headers.get("x-amzn-trace-id")
    if amzn:
        for part in amzn.split(";"):
            if part.strip().startswith("Root="):
                return part.strip()[5:]
    return request.headers.get("x-request-id") or uuid.uuid4().hex


def _client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[-1].strip()
    return request.client.host if request.client else "-"


def install(app: FastAPI) -> None:
    @app.middleware("http")
    async def _observe(request: Request, call_next):
        rid = _request_id(request)
        token = request_id_var.set(rid)
        # ServerErrorMiddleware は自作ミドルウェアの外側にあり、
        # そこへ到達する頃には ContextVar が reset 済みになる。
        # 未捕捉例外ハンドラから参照できるよう request.state にも持たせる。
        request.state.request_id = rid
        excluded = request.url.path in EXCLUDE
        start = time.perf_counter()
        status = 500
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["x-request-id"] = rid
            return response
        finally:
            if not excluded:
                elapsed = time.perf_counter() - start
                route = request.scope.get("route")
                path = getattr(route, "path", request.url.path)
                REQUESTS.labels(request.method, path, str(status)).inc()
                LATENCY.labels(request.method, path).observe(elapsed)
                log.info("access", extra={"fields": {
                    "method": request.method, "path": path, "status": status,
                    "duration_ms": round(elapsed * 1000, 2), "client_ip": _client_ip(request),
                }})
            request_id_var.reset(token)

    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
