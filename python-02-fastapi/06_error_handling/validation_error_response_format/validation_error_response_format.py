"""
学習ポイント: バリデーションエラーのレスポンス形式カスタマイズ
- RequestValidationError: Pydanticバリデーション失敗時の例外
- exception_handler      : バリデーションエラーのレスポンスをカスタマイズ
- エラー詳細の整形        : フィールド名・入力値・エラーメッセージを分かりやすく返す
"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for error in exc.errors():
        errors.append({
            "field":   " -> ".join(str(loc) for loc in error["loc"] if loc != "body"),
            "message": error["msg"],
            "input":   error.get("input"),
        })
    return JSONResponse(
        status_code=422,
        content={"status": "validation_error", "errors": errors},
    )

class ItemCreate(BaseModel):
    name:  str   = Field(min_length=2, max_length=20)
    price: int   = Field(gt=0)
    email: str

@app.post("/items")
async def create_item(item: ItemCreate):
    return item
