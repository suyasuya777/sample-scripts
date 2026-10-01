"""
学習ポイント: 失敗の返し方を1か所に集約する
- HTTPException           : 意図した失敗。そのまま統一形式に整える
- RequestValidationError  : 422。どのフィールドが悪いかを返す
- 未捕捉例外              : 500。スタックトレースは返さず、ログに残す
- 共通       : レスポンスに request_id を含め、問い合わせ時の起点にする

SRE 的な論点:
  未捕捉例外をそのまま外に出すと、スタックトレースに内部のパス・モジュール構成・
  時にはクエリや接続文字列まで載る。攻撃者にとっては地図になる。
  一方でログには全部残さないと調査できない。「外には出さず、内には残す」を
  例外ハンドラで徹底する。
"""
import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

log = logging.getLogger("app")
app = FastAPI()


def error_body(code: str, message: str, request: Request, detail=None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "detail": detail,
            "request_id": request.headers.get("x-request-id", "-"),
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    # 意図した失敗。4xx は warning 止まりにし、アラート対象にしない
    level = logging.WARNING if exc.status_code < 500 else logging.ERROR
    log.log(level, "http_exception", extra={"fields": {
        "status": exc.status_code, "path": request.url.path}})
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(f"HTTP_{exc.status_code}", str(exc.detail), request),
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    fields = [
        {"field": ".".join(str(p) for p in e["loc"][1:]), "reason": e["msg"]}
        for e in exc.errors()
    ]
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_body("VALIDATION_ERROR", "入力値が不正です", request, fields),
    )


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception):
    # ログにはスタックトレースを残す
    log.error("unhandled_exception", exc_info=True,
              extra={"fields": {"path": request.url.path}})
    # レスポンスには出さない
    return JSONResponse(
        status_code=500,
        content=error_body("INTERNAL_ERROR", "サーバ内部エラー", request),
    )


@app.get("/boom")
async def boom():
    raise ValueError("secret detail that must not leak")


@app.get("/notfound")
async def notfound():
    raise HTTPException(status_code=404, detail="order not found")
