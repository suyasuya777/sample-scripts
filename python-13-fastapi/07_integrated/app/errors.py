"""統一エラー形式（04_failure/exception_handlers）"""
import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .context import request_id_var

log = logging.getLogger("app")


def _rid(request: Request) -> str:
    """ContextVar を優先し、reset 済みなら request.state から拾う"""
    rid = request_id_var.get()
    if rid == "-":
        rid = getattr(request.state, "request_id", "-")
    return rid


def _body(code: str, message: str, request: Request, detail=None) -> dict:
    return {"error": {"code": code, "message": message,
                      "detail": detail, "request_id": _rid(request)}}


def install(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def _http(request: Request, exc: HTTPException):
        level = logging.WARNING if exc.status_code < 500 else logging.ERROR
        log.log(level, "http_exception", extra={"fields": {"status": exc.status_code}})
        return JSONResponse(status_code=exc.status_code,
                            content=_body(f"HTTP_{exc.status_code}", str(exc.detail), request),
                            headers=getattr(exc, "headers", None))

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError):
        fields = [{"field": ".".join(str(p) for p in e["loc"][1:]), "reason": e["msg"]}
                  for e in exc.errors()]
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            content=_body("VALIDATION_ERROR", "入力値が不正です", request, fields))

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        log.error("unhandled_exception", exc_info=True,
                  extra={"fields": {"path": request.url.path}})
        return JSONResponse(status_code=500, content=_body("INTERNAL_ERROR", "サーバ内部エラー", request))
