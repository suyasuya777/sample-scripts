"""
学習ポイント: カスタム例外ハンドラーの実装
- @app.exception_handler(): 特定例外クラスをキャッチしてレスポンスを返す
- カスタム例外クラス       : アプリ固有のエラーを定義
- 統一エラーフォーマット   : 全例外を同じ構造のJSONで返す
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

class AppException(Exception):
    def __init__(self, status_code: int, error_code: str, message: str):
        self.status_code = status_code
        self.error_code  = error_code
        self.message     = message

class ItemNotFoundException(AppException):
    def __init__(self, item_id: int):
        super().__init__(404, "ITEM_NOT_FOUND", f"Item {item_id} not found")

class InsufficientStockException(AppException):
    def __init__(self):
        super().__init__(409, "INSUFFICIENT_STOCK", "在庫が不足しています")

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "error_code": exc.error_code, "message": exc.message},
    )

@app.get("/items/{item_id}")
async def get_item(item_id: int):
    if item_id == 0:
        raise ItemNotFoundException(item_id)
    if item_id == 99:
        raise InsufficientStockException()
    return {"id": item_id, "name": "PC"}
